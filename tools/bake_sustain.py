import argparse

import pretty_midi


def sustain_intervals(control_changes, threshold):
    intervals = []
    start = None

    for cc in sorted(control_changes, key=lambda item: item.time):
        if cc.number != 64:
            continue

        if cc.value >= threshold and start is None:
            start = cc.time
        elif cc.value < threshold and start is not None:
            if cc.time > start:
                intervals.append((start, cc.time))
            start = None

    if start is not None:
        intervals.append((start, None))

    return intervals


def pedal_end_for_note(note, intervals, midi_end):
    for start, end in intervals:
        end = midi_end if end is None else end
        if start <= note.end < end:
            return end
    return note.end


def bake_instrument_sustain(instrument, midi_end, threshold, remove_sustain):
    intervals = sustain_intervals(instrument.control_changes, threshold)
    if not intervals:
        return

    notes_by_pitch = {}
    for note in instrument.notes:
        notes_by_pitch.setdefault(note.pitch, []).append(note)

    for pitch_notes in notes_by_pitch.values():
        pitch_notes.sort(key=lambda note: (note.start, note.end))

        for index, note in enumerate(pitch_notes):
            baked_end = pedal_end_for_note(note, intervals, midi_end)
            if index + 1 < len(pitch_notes):
                baked_end = min(baked_end, pitch_notes[index + 1].start)
            note.end = max(note.end, baked_end)

    if remove_sustain:
        instrument.control_changes = [
            cc for cc in instrument.control_changes if cc.number != 64
        ]


def main():
    parser = argparse.ArgumentParser(
        description="Extend MIDI note durations according to sustain pedal CC64."
    )
    parser.add_argument("input", help="input MIDI path")
    parser.add_argument("output", help="output MIDI path")
    parser.add_argument(
        "--threshold",
        type=int,
        default=64,
        help="CC64 value treated as pedal down, default: 64",
    )
    parser.add_argument(
        "--keep-sustain",
        action="store_true",
        help="keep original CC64 messages in the output MIDI",
    )
    args = parser.parse_args()

    midi = pretty_midi.PrettyMIDI(args.input)
    midi_end = midi.get_end_time()

    for instrument in midi.instruments:
        bake_instrument_sustain(
            instrument,
            midi_end=midi_end,
            threshold=args.threshold,
            remove_sustain=not args.keep_sustain,
        )

    midi.write(args.output)


if __name__ == "__main__":
    main()
