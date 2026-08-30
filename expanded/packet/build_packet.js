const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, ShadingType, BorderStyle, AlignmentType,
  LevelFormat,
} = require("docx");

const PAGE_W = 12240, PAGE_H = 15840; // US Letter, DXA
const MARGIN = 720; // 0.5in

const NAVY = "1F3864";
const GRAY = "595959";

const h1 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_1,
  spacing: { before: 200, after: 120 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: NAVY, space: 4 } },
  children: [new TextRun({ text, bold: true, color: NAVY, size: 26 })],
});

const h2 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_2,
  spacing: { before: 160, after: 80 },
  children: [new TextRun({ text, bold: true, color: NAVY, size: 21 })],
});

const body = (text, opts = {}) => new Paragraph({
  spacing: { after: 100, line: 264 },
  children: [new TextRun({ text, size: 20, ...opts })],
});

const bullet = (text) => new Paragraph({
  numbering: { reference: "bullets", level: 0 },
  spacing: { after: 60, line: 252 },
  children: [new TextRun({ text, size: 20 })],
});

const numbered = (text) => new Paragraph({
  numbering: { reference: "steps", level: 0 },
  spacing: { after: 70, line: 252 },
  children: [new TextRun({ text, size: 20 })],
});

const boldBullet = (lead, rest) => new Paragraph({
  numbering: { reference: "bullets", level: 0 },
  spacing: { after: 80, line: 252 },
  children: [
    new TextRun({ text: lead, bold: true, size: 20 }),
    new TextRun({ text: rest, size: 20 }),
  ],
});

function cell(text, opts = {}) {
  return new TableCell({
    width: { size: opts.width || 2700, type: WidthType.DXA },
    margins: { top: 40, bottom: 40, left: 100, right: 100 },
    shading: opts.header ? { type: ShadingType.CLEAR, fill: NAVY } : undefined,
    children: [new Paragraph({
      spacing: { after: 0 },
      children: [new TextRun({
        text,
        size: opts.header ? 18 : 16,
        bold: !!opts.header,
        color: opts.header ? "FFFFFF" : "000000",
      })],
    })],
  });
}

const conferenceRows = [
  ["Big Ten", "18", "P5"],
  ["SEC", "16", "P5"],
  ["Big 12", "16", "P5"],
  ["ACC (incl. Notre Dame)", "18", "P5"],
  ["Pac-12 remnant", "2", "P5"],
  ["Big East (non-football)", "10", "non-P5"],
  ["West Coast Conference", "2", "non-P5"],
  ["Summit League", "1", "non-P5"],
];

const confTable = new Table({
  width: { size: 10800, type: WidthType.DXA },
  columnWidths: [5400, 2700, 2700],
  rows: [
    new TableRow({
      tableHeader: true,
      children: [
        cell("Conference", { header: true, width: 5400 }),
        cell("Schools", { header: true, width: 2700 }),
        cell("Tier", { header: true, width: 2700 }),
      ],
    }),
    ...conferenceRows.map(([name, n, tier]) => new TableRow({
      children: [cell(name, { width: 5400 }), cell(n, { width: 2700 }), cell(tier, { width: 2700 })],
    })),
  ],
});

const doc = new Document({
  numbering: {
    config: [
      { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 320, hanging: 220 } } } }] },
      { reference: "steps", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 260 } } } }] },
    ],
  },
  sections: [{
    properties: {
      page: {
        size: { width: PAGE_W, height: PAGE_H },
        margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN },
      },
    },
    children: [
      new Paragraph({
        spacing: { after: 20 },
        children: [new TextRun({ text: "NCAA REVENUE, NIL & OUTCOMES", bold: true, size: 34, color: NAVY })],
      }),
      new Paragraph({
        spacing: { after: 180 },
        children: [new TextRun({ text: "Zach Keller  ·  Expanded Multi-Sport Analysis  ·  ", size: 19, color: GRAY }),
          new TextRun({ text: "github.com/kellerzachary117/ncaa-revenue-analysis", size: 19, color: GRAY, italics: true })],
      }),

      h1("Overview"),
      body("An expanded follow-on to the original 30-school NCAA Revenue Allocation Analysis: the full population of Power 4 + Pac-12-remnant conference schools, plus 13 non-P5 schools known for prominent basketball or other-sport programs, tested across four sports (football, basketball, volleyball, and a men's-soccer equalizer for schools without football). Tests whether revenue and NIL valuation predict wins and graduation outcomes, and whether the answer differs by sport."),

      h1("Schools Analyzed: 83 schools, 249 school-sport rows"),
      body("Full population, not a sample, across the conferences below. \"Power 5\" is used loosely here: the historical Pac-12 dissolved to a 2-school remnant by 2024-25, and the newly announced Pac-12 doesn't launch until 2026-27, after this project's data window."),
      confTable,

      new Paragraph({ children: [new TextRun({ text: "", break: 1 })], spacing: { after: 40 } }),
      h1("Key Findings"),
      boldBullet("Scholarship reinvestment explains football's revenue effect. ", "On its own, more football revenue significantly predicts a LOWER Graduation Success Rate (p = 0.004). But once scholarship/aid investment share is added to the model, that revenue effect stops being significant (p = 0.328), while aid share itself becomes a significant positive predictor (p = 0.029). It isn't that football money hurts academics; it's that big-revenue programs that don't reinvest proportionally in aid have worse outcomes, replicating the original 30-school project's core finding at this larger scale, and pinpointing it specifically to football."),
      boldBullet("Revenue predicts wins, but it depends heavily on the sport. ", "Basketball (p < 0.001) and volleyball (p = 0.005) both show real, significant revenue-to-wins relationships. Football's is only marginal (p = 0.075); soccer shows none (small sample)."),
      boldBullet("NIL valuation predicts wins, not grades, and it's concentrated. ", "Among schools that actually have a player in On3's national NIL 100, a higher NIL valuation significantly predicts a higher win percentage (p = 0.005), but has no relationship with graduation rate (p = 0.584). Revenue itself strongly predicts whether a school has any NIL-100 presence at all (p < 0.001): NIL visibility concentrates at the schools that are already the wealthiest, it doesn't spread opportunity more evenly."),
      boldBullet("Real corrections made along the way, not smoothed over. ", "Three Big East schools assumed \"no football\" (Butler, Georgetown, Villanova) actually sponsor real FCS programs, confirmed against the source data and corrected before analysis. A circulating NIL \"team rankings\" dataset turned out to be from November 2023, not current, and was discarded rather than used."),

      h1("How It Was Built"),
      numbered("Verified the real 2024-25 conference map live (Big Ten, SEC, Big 12, ACC, and a 2-school Pac-12 remnant post-realignment), rather than assuming today's alignment applied retroactively to the data year."),
      numbered("Pulled real EADA AY2023-24 by-sport revenue, expense, and participant data (the most recent year actually published) for all four sports across all ~2,037 Title IV institutions via the site's live data API, then filtered to the 83-school sample."),
      numbered("Cross-checked football sponsorship against the actual EADA data rather than assuming from conference membership: caught three non-football-assumed schools that really do sponsor FCS football, and confirmed the true no-football group before picking men's soccer as its equalizer sport."),
      numbered("Pulled real 2025-26 season win-loss records from NCAA's official stats site and conference standings sources."),
      numbered("Pulled real NCAA Graduation Success Rate data (2018 entering cohort) for the full 83-school population using the GSR database's conference+sport combined search, rather than one-by-one lookups."),
      numbered("Sourced NIL valuation from On3's live NIL 100 rankings (football and basketball only), explicitly restricted in the analysis to schools with real NIL-100 presence rather than treating absence as zero spend."),
      numbered("Pulled institution-level scholarship/aid investment share from a separate EADA data category after confirming, against the raw federal data dictionary, that aid is never reported broken out by individual sport the way revenue and expenses are."),
      numbered("Merged all sources into one school-sport panel and ran the regression models in Python (pandas, statsmodels, robust standard errors)."),

      h2("Languages & Tools"),
      bullet("Python (pandas, statsmodels): data acquisition, merging, and regression modeling"),
      bullet("Git: version control for the full pipeline"),
      bullet("Data sources: US Dept. of Education EADA survey; NCAA Graduation Success Rate database; NCAA official statistics; On3 NIL Valuations"),

      h2("Presenting This"),
      body("Lead with the scholarship-share finding, it's the strongest story: revenue alone looks like it hurts football academics, but that's really scholarship reinvestment doing the work, the same mechanism the original 30-school project found, now pinpointed to one sport. Keep the sport-specific win% split as the second beat. Be upfront that the NIL variable is a real but partial proxy (national top-100 presence), not verified spend; nobody publishes that.", { italics: true, color: GRAY }),
    ],
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(__dirname + "/NCAA_Expanded_Analysis_Packet.docx", buf);
  console.log("wrote NCAA_Expanded_Analysis_Packet.docx");
});
