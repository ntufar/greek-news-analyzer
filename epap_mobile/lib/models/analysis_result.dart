class AnalysisResult {
  final int score;
  final String analysis;
  final int textLength;
  final String source;
  final DateTime timestamp;
  final bool success;
  final String? error;

  AnalysisResult({
    required this.score,
    required this.analysis,
    required this.textLength,
    required this.source,
    required this.timestamp,
    required this.success,
    this.error,
  });

  factory AnalysisResult.fromApi(Map<String, dynamic> json) {
    return AnalysisResult(
      score: 0,
      analysis: json['analysis'] as String? ?? '',
      textLength: json['text_length'] as int? ?? 0,
      source: json['source'] as String? ?? 'Άγνωστη',
      timestamp: DateTime.now(),
      success: json['success'] as bool? ?? false,
      error: json['error'] as String?,
    );
  }

  factory AnalysisResult.error(String message) {
    return AnalysisResult(
      score: 0,
      analysis: '',
      textLength: 0,
      source: '',
      timestamp: DateTime.now(),
      success: false,
      error: message,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'score': score,
      'analysis': analysis,
      'textLength': textLength,
      'source': source,
      'timestamp': timestamp.toIso8601String(),
      'success': success ? 1 : 0,
    };
  }

  factory AnalysisResult.fromMap(Map<String, dynamic> map) {
    return AnalysisResult(
      score: map['score'] as int? ?? 0,
      analysis: map['analysis'] as String? ?? '',
      textLength: map['textLength'] as int? ?? 0,
      source: map['source'] as String? ?? '',
      timestamp: DateTime.parse(map['timestamp'] as String),
      success: (map['success'] as int?) == 1,
    );
  }
}
