import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

class AboutScreen extends StatelessWidget {
  const AboutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Σχετικά')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(12),
        child: Column(
          children: [
            _buildHeader(),
            const SizedBox(height: 16),
            _section(
              context,
              icon: Icons.track_changes,
              title: 'Σκοπός της Εφαρμογής',
              content:
                  'Η εφαρμογή "ΕΠΑΠ" δημιουργήθηκε με στόχο την προστασία των πολιτών '
                  'από την προπαγάνδα και την παραπληροφόρηση. Χρησιμοποιώντας την τεχνητή '
                  'νοημοσύνη Mistral AI, η εφαρμογή αναλύει ελληνικά άρθρα ειδήσεων και '
                  'εντοπίζει στοιχεία προπαγάνδας, προκατάληψης και χειραγώγησης.',
            ),
            const SizedBox(height: 12),
            _section(
              context,
              icon: Icons.search,
              title: 'Χαρακτηριστικά Ανάλυσης',
              isList: true,
              items: const [
                'Εντοπισμός Συναισθηματικής Χειραγώγησης',
                'Αξιολόγηση Προκατάληψης',
                'Ανάλυση Γεγονός vs Άποψη',
                'Αξιοπιστία Πηγής',
                'Τεχνικές Προπαγάνδας',
                'Σύστημα Βαθμολόγησης 1-100',
              ],
            ),
            const SizedBox(height: 12),
            _section(
              context,
              icon: Icons.code,
              title: 'Τεχνολογίες',
              content:
                  'Python 3.8+ • Mistral AI • Vercel Serverless • Flutter • '
                  'BeautifulSoup • Markdown • Mobile-First Design',
            ),
            const SizedBox(height: 12),
            _authorCard(context),
            const SizedBox(height: 12),
            _section(
              context,
              icon: Icons.mobile_friendly,
              title: 'Mobile & PWA Features',
              isList: true,
              items: const [
                'Εγκατάσταση σε Mobile',
                'Share Target - Ανάλυση συνδέσμων από άλλες εφαρμογές',
                'Ιστορικό αναλύσεων',
                'Dark mode',
              ],
            ),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          colors: [Color(0xFF1E3C72), Color(0xFF2A5298)],
        ),
        borderRadius: BorderRadius.vertical(top: Radius.circular(12)),
      ),
      child: const Column(
        children: [
          Text(
            'ΕΠΑΠ',
            style: TextStyle(
              fontSize: 28,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          SizedBox(height: 4),
          Text(
            'Ελληνική Πλατφόρμα Ανάλυσης Παραπληροφόρισης',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 13, color: Colors.white70),
          ),
        ],
      ),
    );
  }

  Widget _section(
    BuildContext context, {
    required IconData icon,
    required String title,
    String? content,
    bool isList = false,
    List<String>? items,
  }) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final headingColor = isDark ? Colors.grey.shade200 : const Color(0xFF1E3C72);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, size: 20, color: headingColor),
                const SizedBox(width: 8),
                Text(
                  title,
                  style: TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.w600,
                    color: headingColor,
                  ),
                ),
              ],
            ),
            if (content != null) ...[
              const SizedBox(height: 10),
              Text(content, style: TextStyle(fontSize: 13, height: 1.6, color: isDark ? Colors.grey.shade300 : const Color(0xFF333333))),
            ],
            if (isList && items != null) ...[
              const SizedBox(height: 10),
              ...items.map(
                (item) => Padding(
                  padding: const EdgeInsets.only(bottom: 6),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Icon(Icons.check_circle, size: 16, color: isDark ? Colors.green.shade300 : Colors.green.shade600),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          item,
                          style: TextStyle(fontSize: 13, color: isDark ? Colors.grey.shade300 : const Color(0xFF333333)),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _authorCard(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            Container(
              width: 60,
              height: 60,
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  colors: [Color(0xFF1E3C72), Color(0xFF2A5298)],
                ),
                shape: BoxShape.circle,
              ),
              alignment: Alignment.center,
              child: const Text(
                'NT',
                style: TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
            ),
            const SizedBox(height: 12),
            const Text(
              'Nicolai Tufar',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: Color(0xFF1E3C72),
              ),
            ),
            const SizedBox(height: 4),
            Text(
              'Developer & Creator',
              style: TextStyle(
                fontSize: 13,
                fontStyle: FontStyle.italic,
                color: isDark ? Colors.grey.shade400 : Colors.grey.shade600,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Η εφαρμογή αναπτύχθηκε για την προστασία των πολιτών από την παραπληροφόρηση στα ελληνικά μέσα ενημέρωσης.',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 13,
                color: isDark ? Colors.grey.shade300 : const Color(0xFF495057),
              ),
            ),
            const SizedBox(height: 12),
            OutlinedButton.icon(
              onPressed: () => launchUrl(Uri.parse('https://github.com/ntufar/epap')),
              icon: const Icon(Icons.code, size: 16),
              label: const Text('GitHub'),
            ),
          ],
        ),
      ),
    );
  }
}
