import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../data/app_data_store.dart';
import '../models/dynasty.dart';
import '../models/historical_event.dart';
import '../models/person.dart';
import '../models/regime.dart';
import '../pages/event_detail_page.dart';
import '../pages/person_detail_page.dart';
import '../widgets/portrait_image.dart';

String _fmtYear(int y) => y < 0 ? '前${-y}' : '$y';

String _yearRange(int s, int e) => '${_fmtYear(s)} – ${_fmtYear(e)}';

void showDynastyDetail(BuildContext context, Dynasty dynasty) {
  showModalBottomSheet(
    context: context,
    isScrollControlled: true,
    builder: (ctx) => DraggableScrollableSheet(
      initialChildSize: 0.65,
      minChildSize: 0.4,
      maxChildSize: 0.95,
      expand: false,
      builder: (_, scrollController) => DynastyDetailSheet(
        dynasty: dynasty,
        scrollController: scrollController,
      ),
    ),
  );
}

class DynastyDetailSheet extends StatelessWidget {
  const DynastyDetailSheet({
    super.key,
    required this.dynasty,
    required this.scrollController,
  });

  final Dynasty dynasty;
  final ScrollController scrollController;

  @override
  Widget build(BuildContext context) {
    final store = context.read<AppDataController>().store!;
    final events = store.eventsByDynasty(dynasty.id);
    final persons = store.personsByDynasty(dynasty.id);
    final regimes = store.regimesByDynasty(dynasty.id);
    final brightness = Theme.of(context).brightness;
    final color = dynasty.colorFor(brightness);

    return ListView(
      controller: scrollController,
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 32),
      children: [
        _Header(dynasty: dynasty, color: color),
        const SizedBox(height: 8),
        if (dynasty.summary != null && dynasty.summary!.isNotEmpty) ...[
          Text(
            dynasty.summary!,
            style: Theme.of(context).textTheme.bodyMedium,
          ),
          const SizedBox(height: 16),
        ],
        if (regimes.isNotEmpty) ...[
          _SectionTitle('政权 ${regimes.length}'),
          _RegimeChips(regimes: regimes, brightness: brightness),
          const SizedBox(height: 16),
        ],
        if (events.isNotEmpty) ...[
          _SectionTitle('事件 ${events.length}'),
          ...events.map((e) => _EventTile(event: e, color: color)),
          const SizedBox(height: 16),
        ],
        if (persons.isNotEmpty) ...[
          _SectionTitle('人物 ${persons.length}'),
          _PersonChips(persons: persons, color: color),
        ],
      ],
    );
  }
}

class _Header extends StatelessWidget {
  const _Header({required this.dynasty, required this.color});

  final Dynasty dynasty;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Container(
          width: 6,
          height: 32,
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(2),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                dynasty.name,
                style: Theme.of(context).textTheme.displayMedium,
              ),
              const SizedBox(height: 2),
              Text(
                _yearRange(dynasty.startYear, dynasty.endYear),
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _SectionTitle extends StatelessWidget {
  const _SectionTitle(this.text);
  final String text;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8, top: 4),
      child: Text(
        text,
        style: Theme.of(context).textTheme.titleLarge,
      ),
    );
  }
}

class _EventTile extends StatelessWidget {
  const _EventTile({required this.event, required this.color});
  final HistoricalEvent event;
  final Color color;

  @override
  Widget build(BuildContext context) {
    final hasBody = event.body != null && event.body!.trim().isNotEmpty;
    return InkWell(
      onTap: () {
        Navigator.of(context).push(
          MaterialPageRoute(
            builder: (_) => EventDetailPage(eventId: event.id),
          ),
        );
      },
      borderRadius: BorderRadius.circular(8),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 4),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SizedBox(
              width: 64,
              child: Text(
                _fmtYear(event.year),
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: color,
                      fontWeight: FontWeight.w600,
                    ),
              ),
            ),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          event.name,
                          style: Theme.of(context).textTheme.titleLarge,
                        ),
                      ),
                      if (hasBody)
                        Icon(Icons.article_outlined,
                            size: 16,
                            color: Theme.of(context).hintColor),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    event.summary,
                    style: Theme.of(context).textTheme.bodyMedium,
                    maxLines: 3,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _RegimeChips extends StatelessWidget {
  const _RegimeChips({required this.regimes, required this.brightness});
  final List<Regime> regimes;
  final Brightness brightness;

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: regimes.map((r) {
        final c = r.colorFor(brightness);
        return Container(
          padding:
              const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
          decoration: BoxDecoration(
            color: c.withValues(alpha: 0.15),
            border: Border.all(color: c, width: 1),
            borderRadius: BorderRadius.circular(4),
          ),
          child: Text(
            '${r.name} ${_yearRange(r.startYear, r.endYear)}',
            style: Theme.of(context).textTheme.bodySmall,
          ),
        );
      }).toList(),
    );
  }
}

class _PersonChips extends StatelessWidget {
  const _PersonChips({required this.persons, required this.color});
  final List<Person> persons;
  final Color color;

  @override
  Widget build(BuildContext context) {
    // Show portrait-having persons first.
    final sorted = [...persons]..sort((a, b) {
      final ap = a.portrait != null ? 0 : 1;
      final bp = b.portrait != null ? 0 : 1;
      return ap.compareTo(bp);
    });
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: sorted.map((p) => _PersonChip(person: p, color: color)).toList(),
    );
  }
}

class _PersonChip extends StatelessWidget {
  const _PersonChip({required this.person, required this.color});
  final Person person;
  final Color color;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final thumbRel = person.portraitThumb ?? person.portrait;
    return Material(
      color: Colors.transparent,
      child: InkWell(
        borderRadius: BorderRadius.circular(20),
        onTap: () {
          Navigator.of(context).push(
            MaterialPageRoute(
              builder: (_) => PersonDetailPage(personId: person.id),
            ),
          );
        },
        child: Container(
          padding: thumbRel != null
              ? const EdgeInsets.fromLTRB(4, 4, 10, 4)
              : const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
          decoration: BoxDecoration(
            border: Border.all(color: color.withValues(alpha: 0.35)),
            borderRadius: BorderRadius.circular(20),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (thumbRel != null) ...[
                ClipOval(
                  child: SizedBox(
                    width: 28,
                    height: 28,
                    child: PortraitImage(
                      relPath: thumbRel,
                      fit: BoxFit.cover,
                      placeholderColor: color.withValues(alpha: 0.2),
                    ),
                  ),
                ),
                const SizedBox(width: 6),
              ],
              Text(
                person.name,
                style: theme.textTheme.bodySmall,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
