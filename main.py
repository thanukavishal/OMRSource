from pathlib import Path

import cv2
import numpy as np
from mido import Message, MidiFile, MidiTrack


MAX_WIDTH = 2000
TICKS_PER_BEAT = 480

MIDI_PITCHES = {
    "C4": 60,
    "D4": 62,
    "E4": 64,
    "F4": 65,
    "G4": 67,
    "A4": 69,
    "B4": 71,
    "C5": 72,
    "D5": 74,
    "E5": 76,
    "F5": 77,
    "G5": 79,
    "A5": 81,
    "B5": 83,
}

NOTE_DURATIONS = {
    "W": TICKS_PER_BEAT * 4,
    "H": TICKS_PER_BEAT * 2,
    "Q": TICKS_PER_BEAT,
}

NOTE_TYPE_LABELS = {
    "W": "Whole",
    "H": "Half",
    "Q": "Quarter",
}


def get_pitch(cy, top_line, spacing):
    note_positions = [
        ("G5", top_line - spacing),
        ("F5", top_line),
        ("E5", top_line + spacing / 2),
        ("D5", top_line + spacing),
        ("C5", top_line + spacing * 1.5),
        ("B4", top_line + spacing * 2),
        ("A4", top_line + spacing * 2.5),
        ("G4", top_line + spacing * 3),
        ("F4", top_line + spacing * 3.5),
        ("E4", top_line + spacing * 4),
        ("D4", top_line + spacing * 4.5),
        ("C4", top_line + spacing * 5),
    ]
    nearest_note = min(note_positions, key=lambda p: abs(cy - p[1]))
    return nearest_note[0]


def normalize_image(img):
    if img is not None and img.shape[1] > MAX_WIDTH:
        scale = MAX_WIDTH / img.shape[1]
        return cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    return img


def build_midi(detected_notes, output_path):
    mid = MidiFile(ticks_per_beat=TICKS_PER_BEAT)
    track = MidiTrack()
    mid.tracks.append(track)
    track.append(Message("program_change", program=74, time=0))

    success_count = 0
    for note in detected_notes:
        pitch = note["pitch"]
        note_type = note["type"]
        if pitch in MIDI_PITCHES and note_type in NOTE_DURATIONS:
            midi_note = MIDI_PITCHES[pitch]
            duration = NOTE_DURATIONS[note_type]
            track.append(Message("note_on", note=midi_note, velocity=80, time=0))
            track.append(Message("note_off", note=midi_note, velocity=0, time=duration))
            success_count += 1

    mid.save(output_path)
    return success_count


def save_preview(path, image, color=cv2.COLOR_RGB2BGR):
    if color is not None:
        image = cv2.cvtColor(image, color)
    cv2.imwrite(str(path), image)


def process_sheet_music(image_path, output_dir, midi_name="converted_music.mid"):
    image_path = Path(image_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError("Could not read the uploaded image. Please use a PNG, JPG, or JPEG file.")

    img = normalize_image(img)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY_INV,
        51,
        15,
    )

    edges = cv2.Canny(thresh, 50, 150)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

    angles = []
    if lines is not None:
        for rho, theta in lines[:, 0]:
            angle = (theta * 180 / np.pi) - 90
            angles.append(angle)
        median_angle = float(np.median(angles))
    else:
        median_angle = 0

    h_img, w_img = img.shape[:2]
    center = (w_img // 2, h_img // 2)
    rotation = cv2.getRotationMatrix2D(center, median_angle, 1.0)
    deskewed = cv2.warpAffine(thresh, rotation, (w_img, h_img))

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    row_sums = np.sum(deskewed == 255, axis=1)
    threshold_width = img.shape[1] * 0.4
    line_y_coords = np.where(row_sums > threshold_width)[0]

    clean_staff_lines = []
    if len(line_y_coords) > 0:
        current_group = [line_y_coords[0]]
        for y in line_y_coords[1:]:
            if y - current_group[-1] <= 10:
                current_group.append(y)
            else:
                clean_staff_lines.append(int(np.mean(current_group)))
                current_group = [y]
        clean_staff_lines.append(int(np.mean(current_group)))

    if len(clean_staff_lines) >= 2:
        spacing = float(np.mean(np.diff(clean_staff_lines)))
        top_line = clean_staff_lines[0]
        used_fallback_spacing = False
    else:
        spacing = 15.0
        top_line = 300
        used_fallback_spacing = True

    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    staff_lines = cv2.morphologyEx(deskewed, cv2.MORPH_OPEN, horizontal_kernel)

    thicken_h = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 3))
    staff_lines_thickened = cv2.dilate(staff_lines, thicken_h, iterations=1)

    no_staff = cv2.subtract(deskewed, staff_lines_thickened)

    repair_size = max(1, int(spacing * 1.5))
    stem_repair_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, repair_size))
    repaired = cv2.morphologyEx(no_staff, cv2.MORPH_CLOSE, stem_repair_kernel)

    head_repair_size = max(2, int(spacing * 0.25))
    head_repair_kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (head_repair_size, head_repair_size),
    )
    repaired = cv2.morphologyEx(repaired, cv2.MORPH_CLOSE, head_repair_kernel)

    final_cleaned = repaired.copy()
    contours, _ = cv2.findContours(final_cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if h > (spacing * 3.5) and w < (spacing * 0.5):
            cv2.drawContours(final_cleaned, [c], -1, 0, cv2.FILLED)

    output_boxes = img_rgb.copy()

    fatten_height = max(1, int(spacing * 1.5))
    fatten_width = max(3, int(spacing * 0.5))
    kernel_fatten = cv2.getStructuringElement(cv2.MORPH_RECT, (fatten_width, fatten_height))
    fattened_notes = cv2.dilate(final_cleaned, kernel_fatten, iterations=1)

    final_contours, _ = cv2.findContours(
        fattened_notes,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )

    detected_notes = []

    for c in final_contours:
        x, y, w, h = cv2.boundingRect(c)

        if h < 10 or w < 5:
            continue

        if h > (spacing * 6) or w < (spacing * 0.4):
            continue

        padded_roi = final_cleaned[y : y + h, x : x + w]
        ink_coords = cv2.findNonZero(padded_roi)
        if ink_coords is None:
            continue

        ix, iy, iw, ih = cv2.boundingRect(ink_coords)
        if iw == 0 or ih == 0:
            continue

        aspect_ratio = ih / float(iw)
        tight_roi = padded_roi[iy : iy + ih, ix : ix + iw]
        row_sums_local = np.sum(tight_roi == 255, axis=1)
        head_cy_local = int(np.argmax(row_sums_local))

        cy_global = y + iy + head_cy_local
        cx_global = x + ix + iw // 2

        head_radius = (iw // 2) + 2
        head_top = max(0, cy_global - head_radius)
        head_bottom = min(deskewed.shape[0], cy_global + head_radius)
        head_left = max(0, cx_global - head_radius)
        head_right = min(deskewed.shape[1], cx_global + head_radius)

        head_roi_raw = deskewed[head_top:head_bottom, head_left:head_right]
        erode_size = max(3, int(spacing * 0.3))
        erosion_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (erode_size, erode_size))
        eroded_head = cv2.erode(head_roi_raw, erosion_kernel, iterations=1)

        surviving_ink = cv2.countNonZero(eroded_head)
        head_area = head_roi_raw.size
        survival_ratio = surviving_ink / head_area if head_area > 0 else 0

        if aspect_ratio < 1.8:
            note_type = "W"
        elif survival_ratio < 0.10:
            note_type = "H"
        else:
            note_type = "Q"

        pitch = get_pitch(cy_global, top_line, spacing)
        detected_notes.append(
            {
                "x": int(x),
                "y": int(y),
                "width": int(w),
                "height": int(h),
                "type": note_type,
                "typeLabel": NOTE_TYPE_LABELS.get(note_type, "Unknown"),
                "pitch": pitch,
                "midi": MIDI_PITCHES.get(pitch),
            }
        )

    detected_notes.sort(key=lambda note: note["x"])

    for note in detected_notes:
        x = note["x"]
        y = note["y"]
        w = note["width"]
        h = note["height"]
        cv2.rectangle(output_boxes, (x, y), (x + w, y + h), (255, 0, 0), 2)
        label = f"{note['pitch']} {note['type']}"
        cv2.putText(output_boxes, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 0), 1)

    midi_path = output_dir / midi_name
    written_notes = build_midi(detected_notes, midi_path)

    original_path = output_dir / "original.png"
    threshold_path = output_dir / "threshold.png"
    cleaned_path = output_dir / "cleaned.png"
    detected_path = output_dir / "detected.png"

    save_preview(original_path, img_rgb)
    save_preview(threshold_path, thresh, color=None)
    save_preview(cleaned_path, final_cleaned, color=None)
    save_preview(detected_path, output_boxes)

    return {
        "notes": detected_notes,
        "summary": {
            "detectedNotes": len(detected_notes),
            "midiNotes": written_notes,
            "staffLines": len(clean_staff_lines),
            "medianAngle": round(median_angle, 3),
            "spacing": round(spacing, 3),
            "usedFallbackSpacing": used_fallback_spacing,
        },
        "files": {
            "midi": midi_path.name,
            "original": original_path.name,
            "threshold": threshold_path.name,
            "cleaned": cleaned_path.name,
            "detected": detected_path.name,
        },
    }


if __name__ == "__main__":
    result = process_sheet_music("images/img.jpg", ".", "converted_music.mid")
    print(f"Detected {result['summary']['detectedNotes']} notes.")
    print(f"Wrote {result['summary']['midiNotes']} MIDI notes to converted_music.mid.")
