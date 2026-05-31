import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/analysis_provider.dart';
import '../utils/constants.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _urlController = TextEditingController();
  final _textController = TextEditingController();
  final _sourceController = TextEditingController();

  bool _useUrl = true;
  bool _autoAnalyzed = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _checkForSharedContent();
    });
  }

  void _checkForSharedContent() {
    final provider = context.read<AnalysisProvider>();
    if (provider.currentResult != null && !_autoAnalyzed) {
      _autoAnalyzed = true;
      Navigator.pushNamed(context, '/result');
    }
  }

  @override
  void dispose() {
    _urlController.dispose();
    _textController.dispose();
    _sourceController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final provider = context.read<AnalysisProvider>();
    final url = _urlController.text.trim();
    final text = _textController.text.trim();
    final source = _sourceController.text.trim();

    if (_useUrl) {
      if (url.isEmpty) {
        _showError('Παρακαλώ εισάγετε URL άρθρου');
        return;
      }
    } else {
      if (text.isEmpty) {
        _showError('Παρακαλώ εισάγετε κείμενο άρθρου');
        return;
      }
      if (text.length < kMinTextLength) {
        _showError('Το κείμενο πρέπει να έχει τουλάχιστον $kMinTextLength χαρακτήρες');
        return;
      }
    }

    await provider.analyze(
      url: _useUrl ? url : null,
      text: !_useUrl ? text : null,
      source: source.isNotEmpty ? source : null,
    );

    if (mounted && provider.state == AnalysisState.success) {
      Navigator.pushNamed(context, '/result');
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.red.shade700),
    );
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(12),
          child: Column(
            children: [
              _buildHeader(isDark),
              const SizedBox(height: 16),
              _buildInstructions(isDark),
              const SizedBox(height: 16),
              _buildForm(isDark),
              const SizedBox(height: 16),
              _buildWarning(isDark),
              const SizedBox(height: 12),
              Consumer<AnalysisProvider>(
                builder: (context, provider, _) {
                  if (provider.state == AnalysisState.loading) {
                    return _buildLoading();
                  }
                  if (provider.state == AnalysisState.error) {
                    return _buildError(provider.errorMessage);
                  }
                  return const SizedBox.shrink();
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader(bool isDark) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF1E3C72), Color(0xFF2A5298)],
        ),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF1E3C72), Color(0xFF2563EB)],
                  ),
                  borderRadius: BorderRadius.circular(10),
                ),
                alignment: Alignment.center,
                child: const Text(
                  'Ε✓',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.w900,
                    color: Colors.white,
                  ),
                ),
              ),
              const SizedBox(width: 10),
              const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'ΕΠΑΠ',
                    style: TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  Text(
                    'Ελληνική Πλατφόρμα Ανάλυσης Παραπληροφόρισης',
                    style: TextStyle(fontSize: 11, color: Colors.white70),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 8),
          const Text(
            'Ελέγξτε αν ένα άρθρο περιέχει στοιχεία προπαγάνδας',
            style: TextStyle(fontSize: 13, color: Colors.white70),
          ),
          const SizedBox(height: 12),
          OutlinedButton.icon(
            onPressed: () => Navigator.pushNamed(context, '/about'),
            icon: const Icon(Icons.info_outline, size: 16),
            label: const Text('Σχετικά'),
            style: OutlinedButton.styleFrom(
              foregroundColor: Colors.white,
              side: const BorderSide(color: Colors.white38),
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
              textStyle: const TextStyle(fontSize: 13),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInstructions(bool isDark) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF1E1E1E) : const Color(0xFFF1F8E9),
        borderRadius: BorderRadius.circular(10),
        border: const Border(
          left: BorderSide(color: Color(0xFF4CAF50), width: 4),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Οδηγίες Χρήσης',
            style: TextStyle(
              fontSize: 15,
              fontWeight: FontWeight.w600,
              color: isDark ? Colors.green.shade300 : const Color(0xFF2E7D32),
            ),
          ),
          const SizedBox(height: 8),
          _instructionStep(1, 'Επιλέξτε τρόπο εισαγωγής: URL ή επικόλληση κειμένου', isDark),
          _instructionStep(2, 'Προσθέστε την πηγή (προαιρετικά)', isDark),
          _instructionStep(3, 'Πατήστε "Ανάλυση Άρθρου"', isDark),
          _instructionStep(4, 'Διαβάστε την αναφορά με παραδείγματα και συστάσεις', isDark),
        ],
      ),
    );
  }

  Widget _instructionStep(int num, String text, bool isDark) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 20,
            height: 20,
            decoration: const BoxDecoration(
              color: Color(0xFF4CAF50),
              shape: BoxShape.circle,
            ),
            alignment: Alignment.center,
            child: Text(
              '$num',
              style: const TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              text,
              style: TextStyle(
                fontSize: 13,
                color: isDark ? Colors.grey.shade300 : const Color(0xFF424242),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildForm(bool isDark) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Τρόπος Εισαγωγής',
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w600,
                color: isDark ? Colors.grey.shade200 : const Color(0xFF333333),
              ),
            ),
            const SizedBox(height: 8),
            SegmentedButton<bool>(
              segments: const [
                ButtonSegment(value: true, label: Text('URL άρθρου')),
                ButtonSegment(value: false, label: Text('Κείμενο άρθρου')),
              ],
              selected: {_useUrl},
              onSelectionChanged: (set) => setState(() => _useUrl = set.first),
              style: SegmentedButton.styleFrom(
                selectedBackgroundColor: const Color(0xFF1E3C72),
                selectedForegroundColor: Colors.white,
              ),
            ),
            const SizedBox(height: 16),
            if (_useUrl) ...[
              TextField(
                controller: _urlController,
                decoration: const InputDecoration(
                  labelText: 'URL Άρθρου',
                  hintText: 'https://example.com/article',
                  prefixIcon: Icon(Icons.link),
                ),
                keyboardType: TextInputType.url,
                textInputAction: TextInputAction.done,
              ),
            ] else ...[
              TextField(
                controller: _textController,
                decoration: InputDecoration(
                  labelText: 'Κείμενο Άρθρου',
                  hintText: 'Επικολλήστε εδώ το κείμενο του άρθρου...',
                  alignLabelWithHint: true,
                ),
                maxLines: 6,
                maxLength: kMaxTextLength,
                textInputAction: TextInputAction.newline,
              ),
            ],
            const SizedBox(height: 12),
            TextField(
              controller: _sourceController,
              decoration: const InputDecoration(
                labelText: 'Πηγή (προαιρετικό)',
                hintText: 'π.χ. ΕΡΤ, ΣΚΑΪ, ANT1',
                prefixIcon: Icon(Icons.business),
              ),
              textInputAction: TextInputAction.done,
            ),
            const SizedBox(height: 20),
            Consumer<AnalysisProvider>(
              builder: (context, provider, _) {
                return SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: provider.state == AnalysisState.loading
                        ? null
                        : _submit,
                    icon: const Icon(Icons.search),
                    label: const Text('Ανάλυση Άρθρου'),
                  ),
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLoading() {
    return const Card(
      child: Padding(
        padding: EdgeInsets.all(24),
        child: Column(
          children: [
            SizedBox(
              width: 28,
              height: 28,
              child: CircularProgressIndicator(strokeWidth: 3),
            ),
            SizedBox(height: 12),
            Text(
              'Ανάλυση σε εξέλιξη...',
              style: TextStyle(fontSize: 14, color: Colors.grey),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildError(String? message) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            const Icon(Icons.error_outline, color: Colors.red, size: 24),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                message ?? 'Σφάλμα κατά την ανάλυση',
                style: const TextStyle(color: Colors.red, fontSize: 13),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildWarning(bool isDark) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF1E1E1E) : const Color(0xFFFFF7F0),
        borderRadius: BorderRadius.circular(10),
        border: const Border(
          left: BorderSide(color: Color(0xFFF97316), width: 4),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Προειδοποίηση',
            style: TextStyle(
              fontSize: 15,
              fontWeight: FontWeight.w600,
              color: isDark ? Colors.orange.shade300 : const Color(0xFFC2410C),
            ),
          ),
          const SizedBox(height: 6),
          Text(
            'Η παραπληροφόρηση είναι σοβαρό πρόβλημα. Η εφαρμογή παρέχει αναλυτικές πληροφορίες αλλά δεν αντικαθιστά την κριτική σκέψη.',
            style: TextStyle(
              fontSize: 12,
              color: isDark ? Colors.grey.shade400 : const Color(0xFF5D4037),
            ),
          ),
        ],
      ),
    );
  }
}
