import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:share_plus/share_plus.dart';
import '../providers/analysis_provider.dart';
import '../utils/score_extractor.dart';
import '../widgets/score_gauge.dart';
import '../widgets/criteria_card.dart';
import '../widgets/analysis_header.dart';

class ResultScreen extends StatelessWidget {
  const ResultScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<AnalysisProvider>(
      builder: (context, provider, _) {
        final result = provider.currentResult;
        if (result == null) {
          return const Scaffold(
            body: Center(child: Text('Δεν υπάρχουν αποτελέσματα')),
          );
        }

        final parsed = parseAnalysis(result.analysis);

        return Scaffold(
          appBar: AppBar(
            title: const Text('Αποτελέσματα'),
            actions: [
              IconButton(
                icon: const Icon(Icons.share),
                onPressed: () {
                  Share.share(
                    'ΕΠΑΠ Ανάλυση - Βαθμολογία: ${result.score}/100\n\n${result.analysis}',
                  );
                },
              ),
              IconButton(
                icon: const Icon(Icons.home),
                onPressed: () {
                  provider.reset();
                  Navigator.popUntil(context, (route) => route.isFirst);
                },
              ),
            ],
          ),
          body: SingleChildScrollView(
            padding: const EdgeInsets.all(12),
            child: Column(
              children: [
                const SizedBox(height: 8),
                ScoreGauge(score: parsed.score),
                const SizedBox(height: 16),
                AnalysisHeader(
                  score: parsed.score,
                  textLength: result.textLength,
                  source: result.source,
                ),
                const SizedBox(height: 16),
                ...parsed.sections.entries.map(
                  (entry) => CriteriaCard(
                    title: entry.key,
                    content: entry.value,
                  ),
                ),
                const SizedBox(height: 16),
                _buildFullAnalysis(context, parsed.rawMarkdown),
                const SizedBox(height: 24),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildFullAnalysis(BuildContext context, String markdown) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Πλήρης Ανάλυση',
              style: TextStyle(
                fontSize: 15,
                fontWeight: FontWeight.w600,
                color: isDark ? Colors.grey.shade200 : const Color(0xFF1E3C72),
              ),
            ),
            const SizedBox(height: 12),
            MarkdownBody(
              data: markdown,
              styleSheet: MarkdownStyleSheet(
                p: TextStyle(
                  fontSize: 14,
                  height: 1.5,
                  color: isDark ? Colors.grey.shade300 : Colors.black87,
                ),
                h2: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: isDark ? Colors.grey.shade200 : const Color(0xFF1E3C72),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
