"""Independent checks for declared text styling and native gradient stops."""
import math

NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}


def rounded(value):
    return math.floor(value + .5)


def hex_color(value):
    value = value.lstrip("#")
    return ("".join(c * 2 for c in value) if len(value) == 3 else value).upper()


def text_lines(node):
    defaults = {"fontSize": node["fontSize"], "fontFamily": node.get("fontFamily", "Times New Roman"),
                "fill": node.get("fill", "#000000"), "bold": node.get("bold", False),
                "italic": node.get("italic", False), "underline": node.get("underline", False),
                "baselineShift": node.get("baselineShift", "none")}
    lines = [[]]
    for run in node.get("runs", [{"text": node["text"]}]):
        style = {**defaults, **run}
        for index, text in enumerate(run["text"].replace("\r\n", "\n").replace("\r", "\n").split("\n")):
            if index:
                lines.append([])
            if text:
                lines[-1].append({**style, "text": text})
    return lines


def audit_text(obj, node, unit):
    errors = []
    points = lambda value: max(100, rounded(value * unit / 914400 * 7200))
    actual_lines = obj.findall("p:txBody/a:p", NS)
    expected_lines = text_lines(node)
    if len(actual_lines) != len(expected_lines):
        errors.append("paragraph count differs")
    body = obj.find("p:txBody/a:bodyPr", NS)
    if body is None or body.get("wrap") != "none" or body.get("anchor") != ("ctr" if node.get("verticalAlign") == "middle" else "t"):
        errors.append("text wrapping or vertical alignment differs")
    if body is not None and (body.find("a:normAutofit", NS) is not None or body.find("a:spAutoFit", NS) is not None):
        errors.append("unexpected automatic font fitting")
    rich = any(key in node for key in ("runs", "underline", "baselineShift", "lineSpacing"))
    for actual, expected in zip(actual_lines, expected_lines):
        props = actual.find("a:pPr", NS)
        if props is None or props.get("algn") != {"middle": "ctr", "end": "r"}.get(node.get("anchor"), "l"):
            errors.append("paragraph alignment differs")
        runs = actual.findall("a:r", NS)
        if not expected and not rich and len(runs) == 1 and runs[0].findtext("a:t", default="", namespaces=NS) == "":
            runs = []  # Legacy plain-text serializer represents an empty line with one empty run.
        if len(runs) != len(expected):
            errors.append("text run count differs")
        for run, style in zip(runs, expected):
            if run.findtext("a:t", default="", namespaces=NS) != style["text"]:
                errors.append("text run content differs")
            prop = run.find("a:rPr", NS)
            if prop is None:
                errors.append("missing text run properties")
                continue
            desired = {"sz": str(points(style["fontSize"])), "b": str(int(style["bold"])), "i": str(int(style["italic"])),
                       "u": "sng" if style["underline"] else "none",
                       "baseline": str({"none": 0, "super": 30000, "sub": -25000}[style["baselineShift"]])}
            for attr, value in desired.items():
                default = "none" if attr == "u" else "0"
                if prop.get(attr, default) != value:
                    errors.append("text style " + attr + " differs")
            face = style["fontFamily"].split(",")[0].replace('"', "").replace("'", "")
            for tag in ("latin", "ea", "cs"):
                font = prop.find("a:" + tag, NS)
                if font is None or font.get("typeface") != face:
                    errors.append("text font " + tag + " differs")
            color = prop.find("a:solidFill/a:srgbClr", NS)
            if color is None or color.get("val") != hex_color(style["fill"]) or len(color):
                errors.append("text color differs")
        spacing = props.find("a:lnSpc/a:spcPts", NS) if props is not None else None
        if len(expected_lines) > 1 or "lineSpacing" in node:
            largest = max([node["fontSize"]] + [s["fontSize"] for s in expected]) if rich else node["fontSize"]
            wanted = rounded(node["lineSpacing"] * unit / 914400 * 7200) if "lineSpacing" in node else rounded(points(largest) * 1.14)
            if spacing is None or spacing.get("val") != str(wanted):
                errors.append("text line spacing differs")
    return [node["id"] + ": " + error for error in dict.fromkeys(errors)]


def audit_gradient(obj, node):
    gradient = obj.find("p:spPr/a:gradFill", NS)
    expected = node.get("gradient")
    if expected is None:
        return [node["id"] + ": unexpected gradient"] if gradient is not None else []
    errors = []
    if gradient is None:
        return [node["id"] + ": missing native gradient"]
    linear = gradient.find("a:lin", NS)
    angle = rounded(expected["angle"] % 360 * 60000) % 21600000
    if linear is None or linear.get("ang") != str(angle) or linear.get("scaled") != "1" or gradient.get("rotWithShape") != "1":
        errors.append("gradient angle or coordinate mode differs")
    stops = gradient.findall("a:gsLst/a:gs", NS)
    if len(stops) != len(expected["stops"]):
        errors.append("gradient stop count differs")
    for actual, wanted in zip(stops, expected["stops"]):
        color = actual.find("a:srgbClr", NS)
        alpha = color.find("a:alpha", NS) if color is not None else None
        if (actual.get("pos") != str(rounded(wanted["offset"] * 100000)) or color is None
                or color.get("val") != hex_color(wanted["color"])
                or (alpha.get("val") if alpha is not None else "100000") != str(rounded(wanted.get("opacity", 1) * 100000))
                or any(child.tag != "{" + NS["a"] + "}alpha" for child in color)):
            errors.append("gradient stop color, position or opacity differs")
    return [node["id"] + ": " + error for error in dict.fromkeys(errors)]
