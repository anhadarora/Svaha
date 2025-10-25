import 'package:flutter/material.dart';
import 'package:swaha/screens/boardroom/boardroom_screen.dart';
import 'package:swaha/screens/drilldown_screen.dart';
import 'package:swaha/screens/theater/theater_screen.dart';
import 'package:swaha/screens/user_settings/user_settings_screen.dart';
import 'package:swaha/screens/workshop/workshop_screen.dart';
import 'package:swaha/widgets/custom_app_bar.dart';
import 'package:swaha/widgets/custom_bottom_nav_bar.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Swaha',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: const MainScreen(),
    );
  }
}

class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  _MainScreenState createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _selectedIndex = 0;

  final List<GlobalKey<NavigatorState>> _navigatorKeys = [
    GlobalKey<NavigatorState>(),
    GlobalKey<NavigatorState>(),
    GlobalKey<NavigatorState>(),
  ];

  final List<List<String>> _navigationStacks = [
    ['Workshop'],
    ['Theater'],
    ['Boardroom'],
  ];

  void _navigateTo(int index, String screen) {
    _navigatorKeys[index].currentState!.push(
      MaterialPageRoute(
        builder: (context) => DrilldownScreen(parent: _navigationStacks[index].last),
      ),
    );
    setState(() {
      _navigationStacks[index].add(screen);
    });
  }

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  void _onBack() {
    if (_navigatorKeys[_selectedIndex].currentState!.canPop()) {
      _navigatorKeys[_selectedIndex].currentState!.pop();
      setState(() {
        _navigationStacks[_selectedIndex].removeLast();
      });
    }
  }

  void _onSettings() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const UserSettingsScreen(),
      ),
    );
  }

  void _onBreadcrumbTapped(int index) {
    if (index < _navigationStacks[_selectedIndex].length - 1) {
      int count = _navigationStacks[_selectedIndex].length - 1 - index;
      for (int i = 0; i < count; i++) {
        _navigatorKeys[_selectedIndex].currentState!.pop();
      }
      setState(() {
        _navigationStacks[_selectedIndex]
            .removeRange(index + 1, _navigationStacks[_selectedIndex].length);
      });
    }
  }

  List<String> _getBreadcrumbs() {
    return _navigationStacks[_selectedIndex];
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: CustomAppBar(
        breadcrumbs: _getBreadcrumbs(),
        onBack: _onBack,
        onSettings: _onSettings,
        onBreadcrumbTapped: _onBreadcrumbTapped,
      ),
      body: IndexedStack(
        index: _selectedIndex,
        children: [
          Navigator(
            key: _navigatorKeys[0],
            onGenerateRoute: (routeSettings) {
              return MaterialPageRoute(
                builder: (context) => WorkshopScreen(onNavigate: (screen) => _navigateTo(0, screen)),
              );
            },
          ),
          Navigator(
            key: _navigatorKeys[1],
            onGenerateRoute: (routeSettings) {
              return MaterialPageRoute(
                builder: (context) => TheaterScreen(onNavigate: (screen) => _navigateTo(1, screen)),
              );
            },
          ),
          Navigator(
            key: _navigatorKeys[2],
            onGenerateRoute: (routeSettings) {
              return MaterialPageRoute(
                builder: (context) => BoardroomScreen(onNavigate: (screen) => _navigateTo(2, screen)),
              );
            },
          ),
        ],
      ),
      bottomNavigationBar: CustomBottomNavBar(
        selectedIndex: _selectedIndex,
        onItemTapped: _onItemTapped,
      ),
    );
  }
}