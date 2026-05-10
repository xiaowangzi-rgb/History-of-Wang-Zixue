import 'package:flutter/material.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';

import '../data/app_data_store.dart';
import '../models/dynasty.dart';
import '../models/historical_event.dart';
import '../models/person.dart';
import '../widgets/portrait_image.dart';
import 'event_detail_page.dart';

String _fmtYear(int y) => y < 0 ? '前${-y}' : '$y';

class PersonDetailPage extends StatelessWidget {
  const PersonDetailPage({super.key, required this.personId});

  final String personId;

  @override
  Widget build(BuildContext context) {
    final store = context.read<AppDataController>().store!;
    final person = store.personById[personId];
    if (person == null) {
      return Scaffold(
        appBar: AppBar(),
        body: const Center(child: Text('人物不存在')),
      );
    }
    final dynasty = store.dynastyById[person.dynastyId];
    final brightness = Theme.of(context).brightness;
    final color = dynasty?.colorFor(brightness) ??
        Theme.of(context).colorScheme.primary;

    final relatedEvents = _relatedEvents(store, person);

    return Scaffold(
      appBar: AppBar(title: Text(dynasty?.name ?? '')),
      body: ListView(
        padding: EdgeInsets.zero,
        children: [
          if (person.portrait != null)
            _Portrait(relPath: person.portrait!, color: color),
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 20, 20, 32),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _Header(person: person, color: color, dynasty: dynasty),
                const SizedBox(height: 18),
                if (person.summary != null && person.summary!.isNotEmpty)
                  _Summary(text: person.summary!),
                if (person.body != null && person.body!.trim().isNotEmpty) ...[
                  const SizedBox(height: 24),
                  _Body(body: person.body!, color: color),
                ],
                if (relatedEvents.isNotEmpty) ...[
                  const SizedBox(height: 24),
                  Text('相关事件',
                      style: Theme.of(context).textTheme.titleLarge),
                  const SizedBox(height: 8),
                  ...relatedEvents.map(
                    (e) => _EventLink(event: e, color: color),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  List<HistoricalEvent> _relatedEvents(AppDataStore store, Person p) {
    final byParticipants = store.events
        .where((e) => e.participants.contains(p.id))
        .toList();
    if (byParticipants.isNotEmpty) {
      byParticipants.sort((a, b) => a.year.compareTo(b.year));
      return byParticipants;
    }
    // Fallback: events from same dynasty during this person's lifetime
    final start = p.birthYear ?? p.reignStart;
    final end = p.deathYear ?? p.reignEnd;
    if (start == null || end == null) return const [];
    final dyn = store.eventsByDynasty(p.dynastyId);
    return dyn
        .where((e) => e.year >= start - 5 && e.year <= end + 5)
        .toList();
  }
}

class _Portrait extends StatelessWidget {
  const _Portrait({required this.relPath, required this.color});
  final String relPath;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return AspectRatio(
      aspectRatio: 4 / 5,
      child: Stack(
        fit: StackFit.expand,
        children: [
          PortraitImage(
            relPath: relPath,
            fit: BoxFit.cover,
            alignment: const Alignment(0, -0.1),
            placeholderColor: color.withValues(alpha: 0.2),
            errorBuilder: (_) => Container(color: color),
          ),
          DecoratedBox(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [
                  Colors.transparent,
                  Theme.of(context)
                      .scaffoldBackgroundColor
                      .withValues(alpha: 0.0),
                  Theme.of(context).scaffoldBackgroundColor,
                ],
                stops: const [0.0, 0.65, 1.0],
              ),
            ),
          ),
          Positioned(
            top: 0,
            left: 0,
            right: 0,
            child: Container(height: 3, color: color),
          ),
        ],
      ),
    );
  }
}

class _Header extends StatelessWidget {
  const _Header(
      {required this.person, required this.color, required this.dynasty});
  final Person person;
  final Color color;
  final Dynasty? dynasty;

  String _yearLine() {
    final parts = <String>[];
    if (person.birthYear != null && person.deathYear != null) {
      parts.add(
          '${_fmtYear(person.birthYear!)} – ${_fmtYear(person.deathYear!)}');
    } else if (person.reignStart != null && person.reignEnd != null) {
      parts.add(
          '在位 ${_fmtYear(person.reignStart!)} – ${_fmtYear(person.reignEnd!)}');
    }
    if (person.role != null) parts.add(person.role!);
    if (dynasty != null) parts.add(dynasty!.name);
    return parts.join('  ·  ');
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          person.name,
          style: GoogleFonts.notoSerifSc(
            fontSize: 32,
            fontWeight: FontWeight.w700,
            color: color,
            letterSpacing: 2,
            height: 1.2,
          ),
        ),
        const SizedBox(height: 6),
        Text(
          _yearLine(),
          style: GoogleFonts.notoSansSc(
            fontSize: 12,
            color: theme.hintColor,
            letterSpacing: 0.6,
          ),
        ),
      ],
    );
  }
}

class _Summary extends StatelessWidget {
  const _Summary({required this.text});
  final String text;
  @override
  Widget build(BuildContext context) {
    return Text(
      text,
      style: GoogleFonts.notoSerifSc(
        fontSize: 15,
        height: 1.7,
        color: Theme.of(context).colorScheme.onSurface,
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
        h2: base.headlineMedium,
        h3: base.titleLarge,
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

class _EventLink extends StatelessWidget {
  const _EventLink({required this.event, required this.color});
  final HistoricalEvent event;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: () {
        Navigator.of(context).push(
          MaterialPageRoute(
            builder: (_) => EventDetailPage(eventId: event.id),
          ),
        );
      },
      borderRadius: BorderRadius.circular(6),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 8),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SizedBox(
              width: 56,
              child: Text(
                _fmtYear(event.year),
                style: GoogleFonts.notoSansSc(
                  fontSize: 12,
                  color: color.withValues(alpha: 0.85),
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    event.name,
                    style: GoogleFonts.notoSerifSc(
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                      color:
                          Theme.of(context).colorScheme.onSurface,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    event.summary,
                    style: GoogleFonts.notoSansSc(
                      fontSize: 12,
                      color: Theme.of(context).hintColor,
                      height: 1.4,
                    ),
                    maxLines: 2,
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
