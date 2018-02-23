import re;

sZero = "0"; # Normal: "0", slashed: "&#216;", dotted: "&#664;"
asCodePage437_to_HTML = [
  "&#9216;",   "&#9786;",   "&#9787;",   "&#9829;",   "&#9830;",   "&#9827;",   "&#9824;",   "&#8226;",
  "&#9688;",   "&#9675;",   "&#9689;",   "&#9794;",   "&#9792;",   "&#9834;",   "&#9835;",   "&#9788;",
  "&#9658;",   "&#9668;",   "&#8597;",   "&#8252;",   "&#182;",    "&#167;",    "&#9644;",   "&#8616;",
  "&#8593;",   "&#8595;",   "&#8594;",   "&#8592;",   "&#8735;",   "&#8596;",   "&#9650;",   "&#9660;",
  " ",         "!",         "&quot;",    "#",         "$",         "%",         "&amp;",     "'",
  "(",         ")",         "*",         "+",         ",",         "-",         ".",         "/",
  sZero,       "1",         "2",         "3",         "4",         "5",         "6",         "7",
  "8",         "9",         ":",         ";",         "&lt;",      "=",         "&gt;",      "?",
  "@",         "A",         "B",         "C",         "D",         "E",         "F",         "G",
  "H",         "I",         "J",         "K",         "L",         "M",         "N",         "O",
  "P",         "Q",         "R",         "S",         "T",         "U",         "V",         "W",
  "X",         "Y",         "Z",         "[",         "\\",        "]",         "^",         "_",
  "`",         "a",         "b",         "c",         "d",         "e",         "f",         "g",
  "h",         "i",         "j",         "k",         "l",         "m",         "n",         "o",
  "p",         "q",         "r",         "s",         "t",         "u",         "v",         "w",
  "x",         "y",         "z",         "{",         "|",         "}",         "~",         "&#8962;",
  "&#199;",    "&#252;",    "&#233;",    "&#226;",    "&#228;",    "&#224;",    "&#229;",    "&#231;",
  "&#234;",    "&#235;",    "&#232;",    "&#239;",    "&#238;",    "&#236;",    "&#196;",    "&#197;",
  "&#201;",    "&#230;",    "&#198;",    "&#244;",    "&#246;",    "&#242;",    "&#251;",    "&#249;",
  "&#255;",    "&#214;",    "&#220;",    "&#162;",    "&#163;",    "&#165;",    "&#8359;",   "&#402;",
  "&#225;",    "&#237;",    "&#243;",    "&#250;",    "&#241;",    "&#209;",    "&#170;",    "&#186;",
  "&#191;",    "&#8976;",   "&#172;",    "&#189;",    "&#188;",    "&#161;",    "&#171;",    "&#187;",
  "&#9617;",   "&#9618;",   "&#9619;",   "&#9474;",   "&#9508;",   "&#9569;",   "&#9570;",   "&#9558;",
  "&#9557;",   "&#9571;",   "&#9553;",   "&#9559;",   "&#9565;",   "&#9564;",   "&#9563;",   "&#9488;",
  "&#9492;",   "&#9524;",   "&#9516;",   "&#9500;",   "&#9472;",   "&#9532;",   "&#9566;",   "&#9567;",
  "&#9562;",   "&#9556;",   "&#9577;",   "&#9574;",   "&#9568;",   "&#9552;",   "&#9580;",   "&#9575;",
  "&#9576;",   "&#9572;",   "&#9573;",   "&#9561;",   "&#9560;",   "&#9554;",   "&#9555;",   "&#9579;",
  "&#9578;",   "&#9496;",   "&#9484;",   "&#9608;",   "&#9604;",   "&#9612;",   "&#9616;",   "&#9600;",
  "&#945;",    "&#946;",    "&#915;",    "&#960;",    "&#931;",    "&#963;",    "&#956;",    "&#964;",
  "&#934;",    "&#920;",    "&#937;",    "&#948;",    "&#8734;",   "&#966;",    "&#949;",    "&#8745;",
  "&#8801;",   "&#177;",    "&#8805;",   "&#8804;",   "&#8992;",   "&#8993;",   "&#247;",    "&#8776;",
  "&#176;",    "&#8729;",   "&#183;",    "&#8730;",   "&#8319;",   "&#178;",    "&#9632;",   "&#9228;",
];
def fsHTMLCP437(sChar):
  return asCodePage437_to_HTML[ord(sChar)];

if __name__ == "__main__":
  sHTML = "<html><head><style>* { font-family: Courier, monospace; }</style></head><body>\n";
  for uHighNibble in xrange(0, 0x10):
    sHTML += "|";
    for uLowNibble in xrange(0, 0x10):
      sChar = chr(uHighNibble * 16 + uLowNibble);
      sHTML += fsHTMLCP437(sChar);
    sHTML += "|<br/>\n";
  sHTML += "</body></html>\n";
  print sHTML;