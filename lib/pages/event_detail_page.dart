import 'package:flutter/material.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';
import 'package:provider/provider.dart';

import '../data/app_data_store.dart';
import '../models/historical_event.dart';
import '../models/person.dart';
import 'person_detail_page.dart';

String _fmtYear(int y) => y < 0 ? '前${-y}' : '$y';

class EventDetailPage extends StatelessWidget {
  const EventDetailPage({super.key, required this.eventId});

  final String eventId;

  @override
  Widget build(BuildContext context) {
    final store = context.read<AppDataController>().store!;
    final event = store.eventById[eventId];
    if (event == null) {
      return Scaffold(
        appBar: AppBar(),
        body: const Center(child: Text('事件不存在')),
      );
    }
    final dynasty = store.dynastyById[event.dynastyId];
    final brightness = Theme.of(context).brightness;
    final color = dynasty?.colorFor(brightness) ??
        Theme.of(context).colorScheme.primary;
    final hasBody = event.body != null && event.body!.trim().isNotEmpty;

    return Scaffold(
      appBar: AppBar(title: Text(dynasty?.name ?? '')),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(16, 8, 16, 32),
          children: [
            _Header(event: event, color: color),
            const SizedBox(height: 16),
            _Summary(event: event),
            const SizedBox(height: 24),
            if (hasBody)
              _Body(body: event.body!, color: color)
            else
              _BodyPlaceholder(),
            const SizedBox(height: 24),
            if (event.participants.isNotEmpty)
              _Participants(event: event, color: color),
            if (event.locationName != null) ...[
              const SizedBox(height: 16),
              Row(
                children: [
                  Icon(Icons.place_outlined,
                      size: 16,
                      color: Theme.of(context).hintColor),
                  const SizedBox(width: 4),
                  Text(
                    event.locationName!,
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _Header extends StatelessWidget {
  const _Header({required this.event, required this.color});
  final HistoricalEvent event;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.15),
            borderRadius: BorderRadius.circular(4),
          ),
          child: Text(
            _fmtYear(event.year),
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: color,
                  fontWeight: FontWeight.w600,
                ),
          ),
        ),
        const SizedBox(height: 12),
        Text(
          event.name,
          style: Theme.of(context).textTheme.displayLarge,
        ),
      ],
    );
  }
}

class _Summary extends StatelessWidget {
  const _Summary({required this.event});
  final HistoricalEvent event;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        event.summary,
        style: Theme.of(context).textTheme.bodyLarge,
      ),
    );
  }
}

class _Body extends StatelessWidget {
  const _Body({required this.body, required this.color});
  final String body;
  final Color color;

  @override
  Widget build(BuildContext context) {
    final base = Theme.of(context).textTheme;
    return MarkdownBody(
      data: body,
      selectable: true,
      styleSheet: MarkdownStyleSheet(
        p: base.bodyLarge,
        h1: base.displayMedium,
        h2: base.headlineMedium,
        h3: base.titleLarge,
        blockquote: base.bodyMedium?.copyWith(
          fontStyle: FontStyle.italic,
          color: Theme.of(context).hintColor,
        ),
        a: TextStyle(color: color, decoration: TextDecoration.underline),
        blockquoteDecoration: BoxDecoration(
          border: Border(
            left: BorderSide(color: color.withValues(alpha: 0.6), width: 3),
          ),
        ),
        blockquotePadding: const EdgeInsets.only(left: 12, top: 4, bottom: 4),
      ),
    );
  }
}

class _BodyPlaceholder extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        border: Border.all(
          color: Theme.of(context).dividerColor,
          width: 1,
        ),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Icon(Icons.edit_note,
              color: Theme.of(context).hintColor),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              '本事件暂无详细叙述,Phase 1 后期补全。',
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ),
        ],
      ),
    );
  }
}

class _Participants extends StatelessWidget {
  const _Participants({required this.event, required this.color});
  final HistoricalEvent event;
  final Color color;

  @override
  Widget build(BuildContext context) {
    final store = context.read<AppDataController>().store!;
    final persons = event.participants
        .map((id) => store.personById[id])
        .whereType<Person>()
        .toList();
    if (persons.isEmpty) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('参与者',
            style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: 8),
        Wrap(
          spacing: 6,
          runSpacing: 6,
          children: persons.map((p) {
            return InkWell(
              borderRadius: BorderRadius.circular(4),
              onTap: () => Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (_) => PersonDetailPage(personId: p.id),
                ),
              ),
              child: Container(
                padding: const EdgeInsets.symmetric(
                    horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  border:
                      Border.all(color: color.withValues(alpha: 0.4)),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  p.name,
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ),
            );
          }).toList(),
        ),
      ],
    );
  }
}
