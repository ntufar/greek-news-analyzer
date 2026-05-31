import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/analysis_result.dart';
import '../utils/constants.dart';
import '../utils/score_extractor.dart';

class ApiService {
  final String baseUrl;
  final http.Client _client;

  ApiService({String? baseUrl, http.Client? client})
      : baseUrl = baseUrl ?? kApiBaseUrl,
        _client = client ?? http.Client();

  Future<AnalysisResult> analyze({
    String? text,
    String? url,
    String? source,
  }) async {
    try {
      final response = await _client.post(
        Uri.parse('$baseUrl/analyze'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'text': text ?? '',
          'url': url ?? '',
          'source': source ?? '',
        }),
      );

      final data = jsonDecode(response.body) as Map<String, dynamic>;

      if (data['error'] != null) {
        return AnalysisResult.error(data['error'] as String);
      }

      final result = AnalysisResult.fromApi(data);
      final score = extractScore(result.analysis);

      return AnalysisResult(
        score: score,
        analysis: result.analysis,
        textLength: result.textLength,
        source: result.source,
        timestamp: result.timestamp,
        success: result.success,
      );
    } catch (e) {
      return AnalysisResult.error('Σφάλμα σύνδεσης: ${e.toString()}');
    }
  }

  void dispose() {
    _client.close();
  }
}
