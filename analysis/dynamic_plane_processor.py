
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

class DynamicPlaneProcessor:
    """
    Transforms raw financial time-series windows (OHLCV) into normalized,
    motion-compensated coordinate systems using Principal Component Analysis (PCA).
    """
    def __init__(self, config: dict):
        """
        Initializes the processor with configuration parameters.

        Args:
            config (dict): A dictionary containing settings like 'drift_threshold'
                           and 'healing_decay_rate'.
        """
        dynamic_plane_settings = config.get('dynamic_plane_settings', {})
        self.drift_threshold = dynamic_plane_settings.get('drift_threshold', 0.1)
        self.healing_decay_rate = dynamic_plane_settings.get('healing_decay_rate', 0.05)
        
        # Basis vectors are the rows of the rotation matrix (PC1, PC2, PC3)
        self.current_basis_vectors = np.identity(3)
        self.scaler = StandardScaler()

    def _get_point_cloud(self, df_window):
        """
        Constructs the 3D point cloud from the window DataFrame.
        The dimensions are Time, Price (close), and Volume.
        """
        points = np.zeros((len(df_window), 3))
        points[:, 0] = np.arange(len(df_window))  # Time dimension
        points[:, 1] = df_window['close'].values   # Price dimension
        points[:, 2] = df_window['volume'].values   # Volume dimension
        return points

    def process_window(self, df_window):
        """
        Processes a single window of data to produce the transformed features.

        Args:
            df_window (pd.DataFrame): A DataFrame representing the window of
                                      OHLCV data.

        Returns:
            dict: A dictionary containing the transformed features, drift metric,
                  and the state of the basis vectors.
        """
        if len(df_window) < 3:
            # PCA requires more samples than components
            return {
                "features": np.zeros((len(df_window), 3)),
                "drift_metric": 1.0,
                "basis_state": self.current_basis_vectors
            }

        # 1. Create and standardize the point cloud
        point_cloud = self._get_point_cloud(df_window)
        scaled_points = self.scaler.fit_transform(point_cloud)

        # 2. Calculate ideal basis vectors for the current window using PCA
        pca = PCA(n_components=3)
        pca.fit(scaled_points)
        ideal_vectors = pca.components_

        # 3. Correct the sign of eigenvectors for temporal consistency
        for i in range(ideal_vectors.shape[0]):
            dot_product = np.dot(self.current_basis_vectors[i], ideal_vectors[i])
            if dot_product < 0:
                ideal_vectors[i] *= -1
        
        # 4. Calculate drift and apply healing logic
        # Using cosine distance: 1 - cosine_similarity
        drift_metric = 1 - np.mean([np.dot(self.current_basis_vectors[i], ideal_vectors[i]) for i in range(3)])

        if drift_metric > self.drift_threshold:
            # Hard reset if drift is too high (trend break)
            self.current_basis_vectors = ideal_vectors
        else:
            # Apply exponential moving average (healing)
            self.current_basis_vectors = (
                self.current_basis_vectors * (1 - self.healing_decay_rate) +
                ideal_vectors * self.healing_decay_rate
            )
            # Re-orthogonalize the basis vectors after EMA smoothing
            self.current_basis_vectors, _ = np.linalg.qr(self.current_basis_vectors)

        # 5. Transform the data into the new coordinate system
        # The rotation matrix is the transpose of the basis vectors matrix
        rotation_matrix = self.current_basis_vectors.T
        transformed_features = np.dot(scaled_points, rotation_matrix)

        return {
            "features": transformed_features,
            "drift_metric": drift_metric,
            "basis_state": self.current_basis_vectors
        }

    def transform_target_vector(self, last_point, future_point):
        """
        Transforms the target vector into the local coordinate system.

        Args:
            last_point (np.array): The last point of the input window [time, price, volume].
            future_point (np.array): The future target point [time, price, volume].

        Returns:
            np.array: The rotated 3D target vector.
        """
        # Create the raw vector in the original coordinate space
        raw_target_vector = future_point - last_point
        
        # Scale the vector (important: use the same scaler)
        # Note: Scaler expects a 2D array, so we reshape and then take the first row
        scaled_target_vector = self.scaler.transform([raw_target_vector])[0]

        # Rotate the vector using the current basis vectors
        rotation_matrix = self.current_basis_vectors.T
        rotated_target_vector = np.dot(scaled_target_vector, rotation_matrix)
        
        return rotated_target_vector
