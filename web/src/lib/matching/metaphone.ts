/**
 * Primary Double Metaphone code, truncated to 4 letters like the published algorithm.
 * Used only as a bonus when the spelling score is already close. Not a drug-fact source.
 */
export function doubleMetaphone(raw: string): string {
  const word = raw.toUpperCase().replace(/[^A-Z]/g, "");
  if (!word) return "";
  let primary = "";
  let index = 0;
  const at = (offset: number) => word[index + offset] ?? "";

  while (primary.length < 4 && index < word.length) {
    const char = at(0);
    if ("AEIOU".includes(char)) {
      if (index === 0) primary += "A";
      index += 1;
      continue;
    }
    if (char === at(1) && !"CK".includes(char)) {
      index += 1;
      continue;
    }
    switch (char) {
      case "B":
        primary += "P";
        index += at(1) === "B" ? 2 : 1;
        break;
      case "C":
        if (at(1) === "H") {
          primary += "X";
          index += 2;
        } else if ("EIY".includes(at(1))) {
          primary += "S";
          index += 1;
        } else {
          primary += "K";
          index += 1;
        }
        break;
      case "D":
        primary += at(1) === "G" ? "J" : "T";
        index += at(1) === "G" ? 2 : 1;
        break;
      case "F":
      case "V":
        primary += "F";
        index += 1;
        break;
      case "G":
        primary += "EIY".includes(at(1)) ? "J" : "K";
        index += 1;
        break;
      case "H":
        if ("AEIOU".includes(at(1))) primary += "H";
        index += 1;
        break;
      case "J":
        primary += "J";
        index += 1;
        break;
      case "K":
      case "Q":
        primary += "K";
        index += 1;
        break;
      case "L":
        primary += "L";
        index += 1;
        break;
      case "M":
        primary += "M";
        index += 1;
        break;
      case "N":
        primary += "N";
        index += 1;
        break;
      case "P":
        primary += at(1) === "H" ? "F" : "P";
        index += at(1) === "H" ? 2 : 1;
        break;
      case "R":
        primary += "R";
        index += 1;
        break;
      case "S":
        primary += at(1) === "H" ? "X" : "S";
        index += at(1) === "H" ? 2 : 1;
        break;
      case "T":
        primary += at(1) === "H" ? "0" : "T";
        index += at(1) === "H" ? 2 : 1;
        break;
      case "W":
      case "Y":
        if ("AEIOU".includes(at(1))) primary += char;
        index += 1;
        break;
      case "X":
        primary += "KS";
        index += 1;
        break;
      case "Z":
        primary += "S";
        index += 1;
        break;
      default:
        index += 1;
    }
  }
  return primary.slice(0, 4);
}
