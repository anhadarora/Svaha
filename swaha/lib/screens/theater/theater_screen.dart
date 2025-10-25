import 'package:flutter/material.dart';
import 'package:swaha/screens/drilldown_screen.dart';

class TheaterScreen extends StatelessWidget {
  final Function(String) onNavigate; // Add this line

  const TheaterScreen({super.key, required this.onNavigate}); // Add this line

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