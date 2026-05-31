import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../providers/analysis_provider.dart';
import '../models/analysis_result.dart';
import '../utils/constants.dart';
import '../widgets/empty_state.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<AnalysisProvider>().loadHistory();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Ιστορικό'),
        actions: [
          Consumer<AnalysisProvider>(
            builder: (context, provider, _) {
              if (provider.history.isEmpty) return const SizedBox.shrink();
              return IconButton(
                icon: const Icon(Icons.delete_sweep),
                onPressed: () => _confirmClear(context, provider),
              );
            },
          ),
        ],
      ),
      body: Consumer<AnalysisProvider>(
        builder: (context, provider, _) {
          if (!provider.historyLoaded) {
            return const Center(child: CircularProgressIndicator());
          }
          if (provider.history.isEmpty) {
            return const EmptyState(
              icon: Icons.history,
              title: 'Κανένα ιστορικό',
              subtitle: 'Οι αναλύσεις σας θα εμφανίζονται εδώ',
            );
          }
          return ListView.builder(
            padding: const EdgeInsets.all(8),
            itemCount: provider.history.length,
            itemBuilder: (context, index) {
              final result = provider.history[index];
              return _HistoryTile(
                result: result,
                onTap: () {
                  provider.setResult(result);
                  Navigator.pushNamed(context, '/result');
                },
                onDelete: () => provider.deleteFromHistory(index + 1),
              );
            },
          );
        },
      ),
    );
  }

  void _confirmClear(BuildContext context, AnalysisProvider provider) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Εκκαθάριση Ιστορικού'),
        content: const Text('Θέλετε σίγουρα να διαγράψετε όλο το ιστορικό;'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Ακύρωση'),
          ),
          TextButton(
            onPressed: () {
              provider.clearHistory();
              Navigator.pop(ctx);
            },
            child: const Text('Διαγραφή', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }
}

class _HistoryTile extends StatelessWidget {
  final AnalysisResult result;
  final VoidCallback onTap;
  final VoidCallback onDelete;

  const _HistoryTile({
    required this.result,
    required this.onTap,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final color = scoreColor(result.score);
    final dateStr = DateFormat('dd/MM/yyyy HH:mm').format(result.timestamp);

    return Card(
      margin: const EdgeInsets.symmetric(vertical: 4, horizontal: 4),
      child: ListTile(
        onTap: onTap,
        leading: Container(
          width: 48,
          height: 48,
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.15),
            borderRadius: BorderRadius.circular(10),
          ),
          alignment: Alignment.center,
          child: Text(
            result.score.toString(),
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ),
        title: Text(
          result.source.isNotEmpty ? result.source : 'Άγνωστη πηγή',
          style: TextStyle(
            fontWeight: FontWeight.w600,
            fontSize: 14,
            color: isDark ? Colors.grey.shade200 : Colors.black87,
          ),
        ),
        subtitle: Text(
          '${result.textLength} χαρακ. • $dateStr',
          style: TextStyle(
            fontSize: 12,
            color: isDark ? Colors.grey.shade500 : Colors.grey.shade600,
          ),
        ),
        trailing: IconButton(
          icon: Icon(
            Icons.delete_outline,
            color: isDark ? Colors.grey.shade600 : Colors.grey.shade400,
            size: 20,
          ),
          onPressed: onDelete,
        ),
      ),
    );
  }
}
