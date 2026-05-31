import 'package:flutter/material.dart';
import '../utils/constants.dart';

class AnalysisHeader extends StatelessWidget {
  final int score;
  final int textLength;
  final String source;

  const AnalysisHeader({
    super.key,
    required this.score,
    required this.textLength,
    required this.source,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final color = scoreColor(score);

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF1E1E1E) : Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border(
          left: BorderSide(color: color, width: 4),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.verified, color: color, size: 20),
              const SizedBox(width: 8),
              Text(
                'Αποτελέσματα',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                  color: isDark ? Colors.white : Colors.black87,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          _infoRow(context, 'Βαθμολογία', score.toString(), color),
          const SizedBox(height: 6),
          _infoRow(context, 'Μήκος κειμένου', '$textLength χαρακ.', null),
          const SizedBox(height: 6),
          _infoRow(context, 'Πηγή', source, null),
        ],
      ),
    );
  }

  Widget _infoRow(BuildContext context, String label, String value, Color? valueColor) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: 13,
            color: isDark ? Colors.grey.shade400 : Colors.grey.shade600,
          ),
        ),
        Text(
          value,
          style: TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.w600,
            color: valueColor ?? (isDark ? Colors.grey.shade200 : Colors.black87),
          ),
        ),
      ],
    );
  }
}
