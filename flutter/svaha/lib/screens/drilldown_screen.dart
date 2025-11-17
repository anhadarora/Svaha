
import 'package:flutter/material.dart';

class DrilldownScreen extends StatelessWidget {
  final String parent;

  const DrilldownScreen({super.key, required this.parent});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Text('Drilldown Screen from $parent'),
      ),
    );
  }
}
