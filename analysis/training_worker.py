
import os
import time
import json
import pandas as pd
import numpy as np
import logging
import uuid
from multiprocessing import Process, Queue
from datetime import datetime
from PIL import Image

from .image_generator import ImageGenerator
from .dynamic_plane_processor import DynamicPlaneProcessor

class TrainingWorker(Process):
    def __init__(self, config: dict, queue: Queue):
        super().__init__()
        self.config = config
        self.queue = queue
        self.logger = logging.getLogger(__name__)
        self.all_epoch_data = {}
        self.active_heads = []

    def _log(self, message, level='info'):
        log_method = getattr(self.logger, level, self.logger.info)
        log_method(message)
        self.queue.put({"type": "log", "message": message})

    def run(self):
        try:
            self._log("Training worker process started.")
            import tensorflow as tf
            try:
                from vit_keras import vit
                self.vit = vit
            except ImportError:
                self.vit = None
                self._log("vit_keras module not found. ViT architecture will be unavailable.", level='warning')
            except Exception as e:
                self.vit = None
                self._log(f"Error importing vit_keras: {e}", level='warning')

            from sklearn.model_selection import TimeSeriesSplit
            from sklearn.metrics import confusion_matrix
            self.tf = tf
            self.TimeSeriesSplit = TimeSeriesSplit
            self.confusion_matrix = confusion_matrix

            self._log("Loading and filtering data...")
            df = self._load_and_filter_data()
            
            is_dynamic_plane = self.config.get('chart_type') == 'Dynamic 2D Plane'
            
            if not is_dynamic_plane:
                self._log("Calculating labels for image-based model...")
                df = self._calculate_all_labels(df)

            validation_method = self.config.get('validation_method', 'Percentage Split')
            if validation_method == 'Time-Series K-Fold':
                self._run_kfold_cross_validation(df, is_dynamic_plane)
            else:
                self._run_single_train_val(df, is_dynamic_plane)

        except Exception as e:
            self._log(f"An error occurred in the training worker: {e}", level='error')
            import traceback
            self._log(traceback.format_exc(), level='error')
        finally:
            if not hasattr(self, 'final_results'):
                self.final_results = {}
            self.queue.put({"type": "finished", "data": self.final_results})

    def _run_single_train_val(self, df, is_dynamic_plane):
        self._log("Running a single training-validation split.")
        train_df, val_df = self._split_data(df)
        
        if is_dynamic_plane:
            self.plane_processor = DynamicPlaneProcessor(self.config)
            train_dataset = self._create_dynamic_dataset(train_df, is_training=True)
            val_dataset = self._create_dynamic_dataset(val_df, is_training=False)
            input_shape = (self.config.get("input_window_size", 5), 3)
        else:
            self.image_generator = ImageGenerator(self.config)
            train_dataset = self._create_image_dataset(train_df, is_training=True)
            val_dataset = self._create_image_dataset(val_df, is_training=False)
            input_shape = self._get_image_input_shape()

        model = self._build_model(input_shape, is_dynamic_plane)
        model.summary(print_fn=lambda x: self._log(x))

        history = self._train_model(model, train_dataset, val_dataset)
        self.all_epoch_data = history.history

        inference_results = self._generate_predictions(model, val_df, val_dataset, is_dynamic_plane)

        model_path = self._save_model(model)
        self.final_results = self._prepare_summary(model_path, inference_results=inference_results)
        self._log("Single training run finished successfully.")

    def _run_kfold_cross_validation(self, df, is_dynamic_plane):
        k_folds = self.config.get('k_folds', 5)
        self._log(f"Running Time-Series K-Fold cross-validation with {k_folds} splits.")
        tscv = self.TimeSeriesSplit(n_splits=k_folds)
        fold_histories = []
        
        for fold, (train_index, val_index) in enumerate(tscv.split(df)):
            self._log(f"--- Starting Fold {fold + 1}/{k_folds} ---")
            train_df, val_df = df.iloc[train_index], df.iloc[val_index]
            
            if is_dynamic_plane:
                self.plane_processor = DynamicPlaneProcessor(self.config)
                train_dataset = self._create_dynamic_dataset(train_df, is_training=True)
                val_dataset = self._create_dynamic_dataset(val_df, is_training=False)
                input_shape = (self.config.get("input_window_size", 5), 3)
            else:
                self.image_generator = ImageGenerator(self.config)
                train_dataset = self._create_image_dataset(train_df, is_training=True)
                val_dataset = self._create_image_dataset(val_df, is_training=False)
                input_shape = self._get_image_input_shape()

            model = self._build_model(input_shape, is_dynamic_plane)
            if fold == 0: model.summary(print_fn=lambda x: self._log(x))
            
            history = self._train_model(model, train_dataset, val_dataset, fold_num=fold + 1)
            fold_histories.append(history.history)

        self.all_epoch_data = self._aggregate_kfold_histories(fold_histories)
        
        _, last_val_df = self._split_data(df)
        if is_dynamic_plane:
            val_dataset = self._create_dynamic_dataset(last_val_df, is_training=False)
        else:
            val_dataset = self._create_image_dataset(last_val_df, is_training=False)
        
        inference_results = self._generate_predictions(model, last_val_df, val_dataset, is_dynamic_plane)

        model_path = self._save_model(model)
        self.final_results = self._prepare_summary(model_path, is_kfold=True, inference_results=inference_results)
        self._log("K-Fold cross-validation finished successfully.")

    def _generate_predictions(self, model, val_df, val_dataset, is_dynamic_plane):
        if is_dynamic_plane:
            self._log("Decoding Dynamic Plane predictions...")
            # 1. Get true and predicted rotated vectors
            y_pred_rotated = model.predict(val_dataset)
            y_true_rotated = np.concatenate([y for x, y in val_dataset], axis=0)

            # 2. Re-create processor and basis states for the validation set
            val_processor = DynamicPlaneProcessor(self.config)
            window_size = self.config.get("input_window_size", 5)
            horizon = self.config.get("prediction_horizon", 1)
            basis_states = []
            for i in range(len(val_df) - window_size - horizon):
                window_df = val_df.iloc[i : i + window_size]
                processed_output = val_processor.process_window(window_df)
                basis_states.append(processed_output["basis_state"])

            # 3. Perform inverse rotation
            y_pred_world = np.array([pred @ basis for pred, basis in zip(y_pred_rotated, basis_states)])
            y_true_world = np.array([true @ basis for true, basis in zip(y_true_rotated, basis_states)])

            # 4. Extract price component (index 1) and format for results widgets
            true_price_change = y_true_world[:, 1]
            pred_price_change = y_pred_world[:, 1]
            
            # Create a dummy head for results
            self.active_heads = ['label_regression']
            return {
                'label_regression': {
                    'true_sample': true_price_change.tolist(),
                    'pred_sample': pred_price_change.tolist()
                }
            }

        # --- Image-based prediction generation ---
        results = {}
        y_true_dict, y_pred_dict = {}, {}
        for head in self.active_heads: y_true_dict[head] = []
        for _, labels in val_dataset.unbatch():
            for head in self.active_heads: y_true_dict[head].append(labels[head].numpy())
        for head in self.active_heads: y_true_dict[head] = np.array(y_true_dict[head])
        predictions = model.predict(val_dataset)
        if len(self.active_heads) == 1: y_pred_dict[self.active_heads[0]] = predictions
        else:
            for i, head in enumerate(model.output_names): y_pred_dict[head] = predictions[i]
        for head in self.active_heads:
            true_labels, pred_labels = y_true_dict[head], y_pred_dict[head]
            sample_size = min(200, len(true_labels))
            results[head] = {'true_sample': true_labels[:sample_size].tolist(), 'pred_sample': pred_labels[:sample_size].tolist()}
            if 'classification' in head or 'confidence' in head:
                pred_classes = np.argmax(pred_labels, axis=1) if pred_labels.ndim > 1 and pred_labels.shape[1] > 1 else np.round(pred_labels).flatten()
                results[head]['confusion_matrix'] = self.confusion_matrix(true_labels, pred_classes).tolist()
        return results

    def _create_dynamic_dataset(self, df, is_training):
        window_size = self.config.get("input_window_size", 5)
        horizon = self.config.get("prediction_horizon", 1)
        def generator():
            for i in range(len(df) - window_size - horizon):
                window_df = df.iloc[i : i + window_size]
                processed_output = self.plane_processor.process_window(window_df)
                features = processed_output["features"]
                last_point_df = df.iloc[i + window_size - 1]
                future_point_df = df.iloc[i + window_size - 1 + horizon]
                last_point = np.array([i + window_size - 1, last_point_df['close'], last_point_df['volume']])
                future_point = np.array([i + window_size - 1 + horizon, future_point_df['close'], future_point_df['volume']])
                target_vector = self.plane_processor.transform_target_vector(last_point, future_point)
                yield features, target_vector
        output_signature = (self.tf.TensorSpec(shape=(window_size, 3), dtype=self.tf.float32), self.tf.TensorSpec(shape=(3,), dtype=self.tf.float32))
        dataset = self.tf.data.Dataset.from_generator(generator, output_signature=output_signature)
        if is_training: dataset = dataset.shuffle(1000)
        return dataset.batch(self.config.get("training", {}).get("batch_size", 32)).prefetch(self.tf.data.AUTOTUNE)

    def _build_model(self, input_shape, is_dynamic_plane):
        if is_dynamic_plane:
            inputs = self.tf.keras.layers.Input(shape=input_shape)
            x = self.tf.keras.layers.LSTM(64, return_sequences=True)(inputs)
            x = self.tf.keras.layers.LSTM(32)(x)
            x = self.tf.keras.layers.Dense(32, activation='relu')(x)
            outputs = self.tf.keras.layers.Dense(3, name='dynamic_vector_output')(x)
            model = self.tf.keras.Model(inputs=inputs, outputs=outputs)
            self.active_heads = ['dynamic_vector_output']
            return model
        # --- Image-based model building ---
        arch_cfg = self.config.get('backbone', {})
        weights = 'imagenet' if arch_cfg.get('pretrained') else None
        if 'EfficientNet' in arch_cfg['architecture']: backbone = getattr(self.tf.keras.applications, arch_cfg['architecture'])(include_top=False, input_shape=input_shape, weights=weights)
        elif 'ResNet' in arch_cfg['architecture']: backbone = self.tf.keras.applications.ResNet50(include_top=False, input_shape=input_shape, weights=weights)
        elif 'ViT' in arch_cfg['architecture']: backbone = self.vit.vit_b16(image_size=(input_shape[0], input_shape[1]), include_top=False, pretrained=arch_cfg.get('pretrained'))
        else: raise NotImplementedError(f"{arch_cfg['architecture']} not supported.")
        backbone.trainable = not arch_cfg.get('freeze')
        inputs = self.tf.keras.layers.Input(shape=input_shape)
        x = backbone(inputs)
        x = self.tf.keras.layers.GlobalAveragePooling2D()(x)
        head_arch = self.config.get('prediction_heads', {}).get('head_architecture', {})
        x = self.tf.keras.layers.Dense(head_arch.get('hidden_units', 512), activation=head_arch.get('activation', 'relu').lower())(x)
        x = self.tf.keras.layers.Dropout(head_arch.get('dropout', 0.2))(x)
        outputs, heads_cfg = {}, self.config.get('prediction_heads', {})
        if 'Regression' in heads_cfg.get('primary_output', ''): outputs['label_regression'] = self.tf.keras.layers.Dense(1, name='label_regression')(x)
        if 'Classification' in heads_cfg.get('primary_output', ''): outputs['label_classification'] = self.tf.keras.layers.Dense(3 if 'Ternary' in self.config.get('classification_settings',{}).get('class_logic','') else 2, activation='softmax', name='label_classification')(x)
        if heads_cfg.get('auxiliary_heads', {}).get('rally_time'): outputs['label_rally_time'] = self.tf.keras.layers.Dense(1, name='label_rally_time')(x)
        if heads_cfg.get('auxiliary_heads', {}).get('directional_confidence'): outputs['label_directional_confidence'] = self.tf.keras.layers.Dense(1, activation='sigmoid', name='label_directional_confidence')(x)
        self.active_heads = list(outputs.keys())
        return self.tf.keras.Model(inputs=inputs, outputs=outputs)

    def _train_model(self, model, train_ds, val_ds, fold_num=None):
        train_cfg = self.config.get('training', {})
        optimizer = getattr(self.tf.keras.optimizers, train_cfg.get('optimizer', 'Adam'))(learning_rate=float(train_cfg.get('learning_rate', '1e-3')))
        losses, loss_weights = {}, {}
        if self.config.get('chart_type') == 'Dynamic 2D Plane':
            losses = 'mean_squared_error'
        else:
            for head in self.active_heads:
                if 'regression' in head or 'rally_time' in head: losses[head], loss_weights[head] = 'mean_squared_error', 1.0
                elif 'classification' in head: losses[head], loss_weights[head] = 'sparse_categorical_crossentropy', 1.0
                elif 'confidence' in head: losses[head], loss_weights[head] = 'binary_crossentropy', 0.5
        metrics = {h: 'accuracy' for h in self.active_heads if 'classification' in h or 'confidence' in h}
        model.compile(optimizer=optimizer, loss=losses, loss_weights=loss_weights, metrics=metrics)
        class EpochSignalCallback(self.tf.keras.callbacks.Callback):
            def __init__(self, q, log, fold): self.queue, self.logger, self.fold_num = q, log, fold
            def on_epoch_end(self, epoch, logs=None):
                prefix = f"Fold {self.fold_num} | " if self.fold_num else ""
                self.queue.put({"type": "epoch", "data": {"epoch": epoch + 1, **logs}})
                self.logger.info(f"{prefix}Epoch {epoch+1} | loss: {logs.get('loss'):.4f} | val_loss: {logs.get('val_loss'):.4f}")
        early_stopping = self.tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=train_cfg.get('early_stopping_patience', 10), restore_best_weights=True)
        return model.fit(train_ds, validation_data=val_ds, epochs=train_cfg.get('max_epochs', 100), verbose=0, callbacks=[EpochSignalCallback(self.queue, self.logger, fold_num), early_stopping])

    # --- Other helpers ---
    # --- Re-implemented Methods (Inheritance Fix) ---
    def _load_and_filter_data(self):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        metadata_path = os.path.join(project_root, "generated_data", "metadata.json")
        
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
            
        instruments = self.config.get('data_source', {}).get('instruments', [])
        if not instruments:
            self._log("DEBUG: Instruments list is empty! Defaulting to ['ACMESOLAR'] for testing.", level='warning')
            instruments = ["ACMESOLAR"]
            
        self._log(f"DEBUG: Loading data for instruments: {instruments}")
        self._log(f"DEBUG: Project Root: {project_root}")
        
        dfs = []
        for symbol in instruments:
            meta = next((m for m in metadata if m['symbol'] == symbol), None)
            if meta:
                file_path = os.path.join(project_root, "generated_data", meta['parquet_filename'])
                self._log(f"DEBUG: Checking file: {file_path}")
                if os.path.exists(file_path):
                    df = pd.read_parquet(file_path)
                    dfs.append(df)
                    self._log(f"DEBUG: Loaded {len(df)} rows for {symbol}")
                else:
                    self._log(f"DEBUG: File not found: {file_path}", level='error')
            else:
                self._log(f"DEBUG: No metadata found for symbol {symbol}", level='error')
        
        if not dfs:
            raise ValueError("No data loaded for selected instruments.")
        
        # Concat and sort
        combined = pd.concat(dfs)
        if 'date' in combined.columns:
            combined['date'] = pd.to_datetime(combined['date'])
            combined = combined.sort_values('date')
        return combined

    def _resample_data(self, df):
        # Assuming data is already minute-level as per metadata
        return df

    def _calculate_all_labels(self, df):
        horizon = self.config.get("prediction_heads", {}).get("horizon", 1) # Default to 1 if not set
        # Simple Regression Label: Future Return
        df['label_regression'] = df['close'].shift(-horizon) / df['close'] - 1.0
        
        # Simple Classification Label: 1 if positive return
        df['label_classification'] = (df['label_regression'] > 0).astype(int)
        
        # Aux heads placeholders
        df['label_rally_time'] = 0.0
        df['label_directional_confidence'] = 1.0
        
        return df.dropna()

    def _split_data(self, df):
        method = self.config.get('validation_method', 'Percentage Split')
        if method == 'Percentage Split':
            pct = self.config.get('validation_percentage', 20) / 100.0
            split_idx = int(len(df) * (1 - pct))
            return df.iloc[:split_idx], df.iloc[split_idx:]
        else:
            # Fallback
            split_idx = int(len(df) * 0.8)
            return df.iloc[:split_idx], df.iloc[split_idx:]

    def _get_image_input_shape(self):
        h = self.config.get("style_settings", {}).get("target_height", 64)
        w = self.config.get("style_settings", {}).get("target_width", 128)
        return (h, w, 3)

    def _create_image_dataset(self, df, is_training):
        # Simplified generator since we don't have the original base class logic
        window_size = 30 # Default window
        h, w, _ = self._get_image_input_shape()
        
        # We need to ensure we can access self.image_generator
        if not hasattr(self, 'image_generator'):
            self.image_generator = ImageGenerator(self.config)
            
        def generator():
            # For efficiency in test, let's limit iterations
            # But normally we iterate all
            indices = range(len(df) - window_size)
            if is_training:
                # Random sample for training to be faster? No, traverse.
                pass
            
            for i in indices:
                window_df = df.iloc[i : i + window_size]
                # Image generation
                img = self.image_generator.generate_image(window_df)
                img = img.astype(np.float32) / 255.0
                
                # Labels - assume last row's label is the target for this window
                last_row = window_df.iloc[-1]
                
                labels = {
                   'label_regression': [last_row.get('label_regression', 0.0)],
                   'label_classification': [last_row.get('label_classification', 0)],
                   'label_rally_time': [last_row.get('label_rally_time', 0.0)],
                   'label_directional_confidence': [last_row.get('label_directional_confidence', 1.0)]
                }
                
                # Filter active heads
                valid_labels = {k: v for k, v in labels.items() if k in self.active_heads}
                
                yield img, valid_labels

        # Create Output Signature
        output_signature = (
            self.tf.TensorSpec(shape=(h, w, 3), dtype=self.tf.float32),
            {k: self.tf.TensorSpec(shape=(1,), dtype=self.tf.float32) if 'reg' in k or 'rally' in k else self.tf.TensorSpec(shape=(1,), dtype=self.tf.int32)
             for k in self.active_heads}
        )
        
        dataset = self.tf.data.Dataset.from_generator(generator, output_signature=output_signature)
        
        batch_size = self.config.get("training", {}).get("batch_size", 32)
        if is_training:
            dataset = dataset.shuffle(100) # Small shuffle
        
        return dataset.batch(batch_size).prefetch(self.tf.data.AUTOTUNE)

    def _save_model(self, model):
        # Implementation of save model
        model_dir = self.config.get("model_save_path", "models")
        name = self.config.get("experiment_name", "experiment")
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        path = os.path.join(model_dir, f"{name}.keras")
        model.save(path)
        return path

    def _prepare_summary(self, model_path, is_kfold=False, inference_results=None):
        return {
            "experiment_summary": {
                "model_path": model_path,
                "epochs_trained": self.config.get("training", {}).get("max_epochs"),
                "final_loss": 0.0 # Placeholder
            },
            "parameter_configuration": self.config,
            "inference_results": inference_results if inference_results else {}
        }
    
    def _aggregate_kfold_histories(self, histories):
        return {} # Placeholder
