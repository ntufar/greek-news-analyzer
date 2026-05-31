import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'app.dart';
import 'providers/analysis_provider.dart';
import 'services/api_service.dart';
import 'services/database_service.dart';
import 'services/share_handler.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  final apiService = ApiService();
  final databaseService = DatabaseService();
  final shareHandler = ShareHandler();

  runApp(
    _EpapAppRoot(
      apiService: apiService,
      databaseService: databaseService,
      shareHandler: shareHandler,
    ),
  );
}

class _EpapAppRoot extends StatefulWidget {
  final ApiService apiService;
  final DatabaseService databaseService;
  final ShareHandler shareHandler;

  const _EpapAppRoot({
    required this.apiService,
    required this.databaseService,
    required this.shareHandler,
  });

  @override
  State<_EpapAppRoot> createState() => _EpapAppRootState();
}

class _EpapAppRootState extends State<_EpapAppRoot> {
  ThemeMode _themeMode = ThemeMode.system;
  final _navigatorKey = GlobalKey<NavigatorState>();

  String? _pendingSharedText;

  @override
  void initState() {
    super.initState();
    _initShareHandler();
  }

  void _initShareHandler() {
    widget.shareHandler.init(
      onShare: (sharedText) {
        _processSharedText(sharedText);
      },
      onInitialShare: (sharedText) {
        _pendingSharedText = sharedText;
        WidgetsBinding.instance.addPostFrameCallback((_) {
          _processPendingShare();
        });
      },
    );
  }

  void _processSharedText(String text) {
    final context = _navigatorKey.currentContext;
    if (context == null) return;
    final provider = context.read<AnalysisProvider>();
    provider.reset();
    if (text.startsWith('http://') || text.startsWith('https://')) {
      provider.analyze(url: text);
    } else {
      provider.analyze(text: text);
    }
    Navigator.of(context).pushNamed('/result');
  }

  void _processPendingShare() {
    if (_pendingSharedText == null) return;
    _processSharedText(_pendingSharedText!);
    _pendingSharedText = null;
  }

  @override
  void dispose() {
    widget.shareHandler.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(
          create: (_) => AnalysisProvider(
            apiService: widget.apiService,
            databaseService: widget.databaseService,
          ),
        ),
      ],
      child: EpapApp(
        themeMode: _themeMode,
        navigatorKey: _navigatorKey,
      ),
    );
  }
}
