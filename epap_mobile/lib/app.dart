import 'package:flutter/material.dart';
import 'screens/home_screen.dart';
import 'screens/result_screen.dart';
import 'screens/history_screen.dart';
import 'screens/about_screen.dart';
import 'utils/theme.dart';

class EpapApp extends StatelessWidget {
  final ThemeMode themeMode;
  final GlobalKey<NavigatorState>? navigatorKey;

  const EpapApp({
    super.key,
    required this.themeMode,
    this.navigatorKey,
  });

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'ΕΠΑΠ',
      debugShowCheckedModeBanner: false,
      navigatorKey: navigatorKey,
      theme: epapLightTheme(),
      darkTheme: epapDarkTheme(),
      themeMode: themeMode,
      initialRoute: '/',
      routes: {
        '/': (context) => const HomeScreen(),
        '/result': (context) => const ResultScreen(),
        '/history': (context) => const HistoryScreen(),
        '/about': (context) => const AboutScreen(),
      },
    );
  }
}
