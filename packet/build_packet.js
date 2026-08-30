const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, ShadingType, BorderStyle, AlignmentType, PageOrientation,
  LevelFormat, convertInchesToTwip,
} = require("docx");

const PAGE_W = 12240, PAGE_H = 15840; // US Letter, DXA
const MARGIN = 720; // 0.5in

const NAVY = "1F3864";
const GRAY = "595959";
const LIGHT = "F2F2F2";

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

function schoolCell(text, opts = {}) {
  return new TableCell({
    width: { size: 3600, type: WidthType.DXA },
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

const tiers = {
  "FBS": [
    ["Michigan", "$221M"], ["Kansas", "$215M"], ["Michigan State", "$164M"],
    ["BYU", "$130M"], ["Georgia Tech", "$128M"], ["UCF", "$93M"],
    ["Boise State", "$60M"], ["Buffalo", "$42M"], ["Kent State", "$35M"],
    ["Sam Houston State", "$27M"],
  ],
  "FCS": [
    ["Illinois State", "$31M"], ["North Dakota State", "$30M"], ["Missouri State", "$25M"],
    ["UT Chattanooga", "$23M"], ["Marist", "$22M"], ["Valparaiso", "$16M"],
    ["SE Missouri State", "$16M"], ["Prairie View A&M", "$15M"], ["Northwestern State (LA)", "$15M"],
    ["Bethune-Cookman", "$14M"],
  ],
  "D1, no football": [
    ["St. John's (NY)", "$54M"], ["Marquette", "$47M"], ["Loyola Marymount", "$40M"],
    ["High Point", "$33M"], ["Quinnipiac", "$32M"], ["Grand Canyon", "$31M"],
    ["UMass Lowell", "$24M"], ["Belmont", "$23M"], ["Mount St. Mary's", "$19M"],
    ["Texas A&M-Corpus Christi", "$16M"],
  ],
};

const headerRow = new TableRow({
  tableHeader: true,
  children: Object.keys(tiers).map((t) => schoolCell(`${t}  (10 schools)`, { header: true })),
});

const bodyRows = [];
for (let i = 0; i < 10; i++) {
  bodyRows.push(new TableRow({
    children: Object.keys(tiers).map((t) => {
      const [name, rev] = tiers[t][i];
      return schoolCell(`${name}: ${rev}`);
    }),
  }));
}

const schoolTable = new Table({
  width: { size: 10800, type: WidthType.DXA },
  columnWidths: [3600, 3600, 3600],
  rows: [headerRow, ...bodyRows],
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
        children: [new TextRun({ text: "NCAA REVENUE ALLOCATION ANALYSIS", bold: true, size: 34, color: NAVY })],
      }),
      new Paragraph({
        spacing: { after: 180 },
        children: [new TextRun({ text: "Zach Keller  ·  Data Analytics Project  ·  ", size: 19, color: GRAY }),
          new TextRun({ text: "github.com/kellerzachary117/ncaa-revenue-analysis", size: 19, color: GRAY, italics: true })],
      }),

      h1("Overview"),
      body("A regression analysis of the relationship between athletic department revenue, scholarship investment, and student-athlete graduation outcomes across 30 NCAA Division I athletic programs. The sample was built to span the real range of D1 program sizes ($13.7M–$221M in athletic revenue) rather than clustering around one tier of school."),

      h1("Schools Analyzed"),
      body("A stratified random sample (seed 42) of 10 programs from each D1 subdivision, drawn from the full population of 356 D1 athletic programs in the US Department of Education's EADA database, AY2023-24. Stratifying across subdivisions, rather than a pure random draw (which would have skewed toward the ~250 smaller FCS/no-football programs), was a deliberate choice to get real revenue variation into the sample."),
      schoolTable,

      new Paragraph({ children: [new TextRun({ text: "", break: 1 })], spacing: { after: 40 } }),
      h1("Key Findings"),
      boldBullet("Revenue alone doesn't predict outcomes. ", "Raw athletic revenue has no significant relationship with graduation success on its own (p = 0.23). A bigger athletic budget by itself does not predict better academic outcomes."),
      boldBullet("What matters is what a program does with the money. ", "Once scholarship investment (student aid as a share of total revenue) enters the model, both revenue and aid share become significant predictors (p = 0.014 and p = 0.021, R² = 0.23). Revenue and total scholarship dollars are highly correlated (r = 0.79): bigger programs spend more on aid in absolute terms, but it's the share of revenue actually reinvested in student aid that predicts outcomes, not program size by itself."),
      boldBullet("Sport mix matters as much as finances. ", "Programs without football post graduation rates about 5.5 points higher than otherwise-comparable FBS/FCS programs, controlling for revenue and scholarship investment (p = 0.028)."),
      boldBullet("The finding holds under a robustness check. ", "The revenue relationship holds, and strengthens, when Federal Graduation Rate replaces the NCAA's own Graduation Success Rate as the outcome measure (p = 0.002), confirming the result isn't an artifact of one specific outcome metric."),

      h1("How It Was Built"),
      numbered("Sourced real athletic-finance data from the US Dept. of Education's EADA (Equity in Athletics Data Analysis) survey, AY2023-24, the same federal disclosure every D1 athletic department is legally required to file."),
      numbered("Built a stratified random sample of 30 programs (10 FBS, 10 FCS, 10 D1-without-football) in Python (pandas), so the sample would span real variation in program size rather than cluster in one tier."),
      numbered("Hand-collected student-athlete outcome data (Graduation Success Rate, 2018 entering cohort, the most recent cohort with a completed 6-year window) from the NCAA's own GSR database for all 30 sampled schools, since the NCAA does not offer a bulk-download option."),
      numbered("Merged the two sources and engineered variables (log revenue, scholarship investment as a share of revenue, enrollment, D1-subdivision indicators) in Python (pandas)."),
      numbered("Ran a four-model OLS regression in Stata (StataNow/SE 19.5), building from a bivariate baseline up to a full model with subdivision and enrollment controls, plus a robustness check swapping in an alternate outcome measure."),
      numbered("Wrote up methodology, data provenance, and findings; version-controlled the full project (data pipeline, Stata do-file, regression log, writeup) in Git."),

      h2("Languages & Tools"),
      bullet("Python (pandas): data acquisition, sample construction, cleaning, variable construction"),
      bullet("Stata (regress, robust standard errors): the actual regression modeling"),
      bullet("Git: version control for the full pipeline"),
      bullet("Data sources: US Dept. of Education EADA survey; NCAA Graduation Success Rate database"),

      h2("Presenting This"),
      body("Lead with the finding, not the method: revenue alone doesn't move the needle, but how a program reinvests it does. Keep this packet ready as a follow-up, not the opener: the regression tables answer \"can you back that up,\" they're not the headline.", { italics: true, color: GRAY }),
    ],
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(__dirname + "/NCAA_Revenue_Analysis_Packet.docx", buf);
  console.log("wrote NCAA_Revenue_Analysis_Packet.docx");
});
