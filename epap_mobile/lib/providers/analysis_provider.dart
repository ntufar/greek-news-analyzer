import 'package:flutter/material.dart';
import '../models/analysis_result.dart';
import '../services/api_service.dart';
import '../services/database_service.dart';

enum AnalysisState { idle, loading, success, error }

class AnalysisProvider extends ChangeNotifier {
  final ApiService _apiService;
  final DatabaseService _databaseService;

  AnalysisProvider({
    required ApiService apiService,
    required DatabaseService databaseService,
  })  : _apiService = apiService,
        _databaseService = databaseService;

  AnalysisState _state = AnalysisState.idle;
  AnalysisResult? _currentResult;
  String? _errorMessage;
  List<AnalysisResult> _history = [];
  bool _historyLoaded = false;

  AnalysisState get state => _state;
  AnalysisResult? get currentResult => _currentResult;
  String? get errorMessage => _errorMessage;
  List<AnalysisResult> get history => _history;
  bool get historyLoaded => _historyLoaded;

  Future<void> analyze({String? text, String? url, String? source}) async {
    _state = AnalysisState.loading;
    _currentResult = null;
    _errorMessage = null;
    notifyListeners();

    final result = await _apiService.analyze(
      text: text,
      url: url,
      source: source,
    );

    if (result.success) {
      _state = AnalysisState.success;
      _currentResult = result;

      await _databaseService.saveResult(result);
    } else {
      _state = AnalysisState.error;
      _errorMessage = result.error;
    }

    notifyListeners();
  }

  Future<void> loadHistory() async {
    _history = await _databaseService.getHistory();
    _historyLoaded = true;
    notifyListeners();
  }

  Future<void> deleteFromHistory(int id) async {
    await _databaseService.deleteResult(id);
    _history = await _databaseService.getHistory();
    notifyListeners();
  }

  Future<void> clearHistory() async {
    await _databaseService.clearHistory();
    _history = [];
    notifyListeners();
  }

  void setResult(AnalysisResult result) {
    _currentResult = result;
    _state = AnalysisState.success;
    notifyListeners();
  }

  void reset() {
    _state = AnalysisState.idle;
    _currentResult = null;
    _errorMessage = null;
    notifyListeners();
  }

  @override
  void dispose() {
    _apiService.dispose();
    super.dispose();
  }
}
