import 'package:flutter/material.dart';

class WorkshopScreen extends StatelessWidget {
  final Function(String) onNavigate;

  const WorkshopScreen({super.key, required this.onNavigate});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: ElevatedButton(
          onPressed: () {
            onNavigate('Drilldown');
          },
          child: const Text('Go to Drilldown'),
        ),
      ),
    );
  }
}
