import 'package:flutter/material.dart';

class BoardroomScreen extends StatelessWidget {
  final Function(String) onNavigate; // Add this line

  const BoardroomScreen({super.key, required this.onNavigate}); // Add this line

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
