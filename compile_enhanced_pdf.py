import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, HRFlowable, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT

pdf_path = "/Users/mjyogesh/epilepsy_framework/EHR_EpSO_Enhanced_Paper.pdf"
fig_dir = "/Users/mjyogesh/epilepsy_framework"

doc = SimpleDocTemplate(
    pdf_path,
    pagesize=letter,
    rightMargin=45,
    leftMargin=45,
    topMargin=45,
    bottomMargin=45
)

styles = getSampleStyleSheet()

# Typography Styles
title_style = ParagraphStyle(
    'DocTitle',
    parent=styles['Heading1'],
    fontName='Helvetica-Bold',
    fontSize=17,
    leading=21,
    alignment=TA_CENTER,
    textColor=colors.HexColor('#1B365D'),
    spaceAfter=10
)

author_style = ParagraphStyle(
    'DocAuthor',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=9.5,
    leading=13.5,
    alignment=TA_CENTER,
    textColor=colors.HexColor('#2C3E50'),
    spaceAfter=12
)

abstract_heading = ParagraphStyle(
    'AbsHeading',
    parent=styles['Heading2'],
    fontName='Helvetica-Bold',
    fontSize=10.5,
    leading=13,
    alignment=TA_CENTER,
    textColor=colors.HexColor('#1B365D'),
    spaceAfter=5
)

abstract_body = ParagraphStyle(
    'AbsBody',
    parent=styles['Normal'],
    fontName='Times-Italic',
    fontSize=9,
    leading=13,
    alignment=TA_JUSTIFY,
    textColor=colors.HexColor('#2C3E50')
)

h1_style = ParagraphStyle(
    'Heading1_Custom',
    parent=styles['Heading1'],
    fontName='Helvetica-Bold',
    fontSize=12,
    leading=15,
    textColor=colors.HexColor('#1B365D'),
    spaceBefore=12,
    spaceAfter=5,
    keepWithNext=True
)

h2_style = ParagraphStyle(
    'Heading2_Custom',
    parent=styles['Heading2'],
    fontName='Helvetica-Bold',
    fontSize=10.5,
    leading=13.5,
    textColor=colors.HexColor('#2C3E50'),
    spaceBefore=9,
    spaceAfter=4,
    keepWithNext=True
)

body_style = ParagraphStyle(
    'Body_Custom',
    parent=styles['Normal'],
    fontName='Times-Roman',
    fontSize=9.5,
    leading=13.5,
    alignment=TA_JUSTIFY,
    textColor=colors.HexColor('#1A1A1A'),
    spaceAfter=5
)

bullet_style = ParagraphStyle(
    'Bullet_Custom',
    parent=body_style,
    leftIndent=12,
    firstLineIndent=-8,
    spaceAfter=3
)

# Table Styles - Width 510 pt = 7.08 in
th_style = ParagraphStyle(
    'TableHeader',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=8,
    leading=10,
    alignment=TA_LEFT,
    textColor=colors.whitesmoke
)

th_center = ParagraphStyle(
    'TableHeaderCenter',
    parent=th_style,
    alignment=TA_CENTER
)

td_style = ParagraphStyle(
    'TableCell',
    parent=styles['Normal'],
    fontName='Times-Roman',
    fontSize=8,
    leading=10.5,
    alignment=TA_LEFT,
    textColor=colors.HexColor('#1A1A1A')
)

td_center = ParagraphStyle(
    'TableCellCenter',
    parent=td_style,
    alignment=TA_CENTER
)

td_bold = ParagraphStyle(
    'TableCellBold',
    parent=td_style,
    fontName='Times-Bold'
)

td_bold_center = ParagraphStyle(
    'TableCellBoldCenter',
    parent=td_center,
    fontName='Times-Bold'
)

caption_style = ParagraphStyle(
    'Caption',
    parent=styles['Normal'],
    fontName='Helvetica-Oblique',
    fontSize=8,
    leading=11,
    alignment=TA_CENTER,
    textColor=colors.HexColor('#4A5568'),
    spaceBefore=4,
    spaceAfter=8
)

def make_table_cell(text, is_header=False, is_bold=False, align='left'):
    if is_header:
        style = th_center if align == 'center' else th_style
    else:
        if is_bold:
            style = td_bold_center if align == 'center' else td_bold
        else:
            style = td_center if align == 'center' else td_style
    return Paragraph(str(text), style)

def get_base_table_style():
    return TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1B365D')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
    ])

elements = []

# Top Banner
elements.append(Paragraph("EHR-EpSO: ENHANCED RESEARCH PAPER (Q1 REVISION)", ParagraphStyle('HeaderTop', fontName='Helvetica-Bold', fontSize=7.5, alignment=TA_CENTER, textColor=colors.HexColor('#4A5568'))))
elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1B365D'), spaceBefore=2, spaceAfter=10))

# Title & Authors
elements.append(Paragraph("Semantically Intelligent Epilepsy Surveillance: An Ontology-Driven Electronic Health Record Framework Integrating MIMIC-IV v3.1, HL7 FHIR R4, and Machine Learning for Population-Scale Neurological Analytics", title_style))
elements.append(Paragraph("<b>M J Yogesh</b><sup>1</sup> &nbsp;&nbsp;&nbsp;&nbsp; <b>Dr. Karthikeyan J</b><sup>1,*</sup><br/><sup>1</sup>School of Computer Science Engineering and Information Systems, Vellore Institute of Technology, Vellore 632 014, Tamil Nadu, India<br/><i>*Corresponding Authors: yogeshmj.nie@gmail.com, karthikeyan.jk@vit.ac.in</i>", author_style))

# Abstract Box
elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CBD5E0'), spaceBefore=0, spaceAfter=6))
elements.append(Paragraph("ABSTRACT", abstract_heading))
abs_text = (
    "Epilepsy affects over 50 million individuals worldwide, yet existing electronic health record (EHR) systems lack the semantic precision, "
    "ontological structure, and analytical depth required for population-level surveillance and clinical decision support. We present <b>EHR-EpSO</b>, "
    "a public health informatics framework addressing three persistent structural gaps—semantic heterogeneity, poor interoperability, and limited predictive capacity—by "
    "unifying the Epilepsy and Seizure Ontology (EpSO) with HL7 Fast Healthcare Interoperability Resources Release 4 (FHIR R4) standards and a modular machine learning analytics engine. "
    "Validated on the largest publicly available epilepsy cohort drawn from MIMIC-IV v3.1 (4,187 admissions, 3,641 unique patients spanning 2008–2022), "
    "our three-stage ontology alignment pipeline (prefix-tree lookup over 3,847 EpSO concept labels coupled with BioWordVec contextual disambiguation) achieved a concept-resolution rate (CR) "
    "of 94.1% (95% CI: 93.2%–95.0%), significantly outperforming general-purpose clinical NLP tools (MetaMap: 81.4%, QuickUMLS: 84.7%, scispaCy: 86.2%). Furthermore, 99.2% of admissions "
    "generated fully validated FHIR R4 resource bundles (Condition, Observation, MedicationRequest). Evaluated under a rigorous 5-fold stratified cross-validation protocol combined with "
    "an independent held-out test evaluation (n=629), a Transformer-encoder classifier achieved an AUROC of 0.876 (95% CI: 0.856–0.896) for 30-day seizure recurrence and 0.839 (95% CI: 0.815–0.863) "
    "for treatment non-adherence, significantly outperforming XGBoost and BiLSTM baselines (p < 0.01, DeLong's test). Dual-model interpretability using TreeSHAP for XGBoost and Integrated Gradients "
    "for the Transformer revealed prior admission frequency and Medicaid coverage as primary predictors of recurrence and non-adherence, respectively. Systematic ablation studies confirmed that "
    "every pipeline stage contributes significantly to performance. EHR-EpSO offers an open-source, production-scalable foundation for neurological population health analytics."
)
elements.append(Paragraph(abs_text, abstract_body))
elements.append(Spacer(1, 4))
elements.append(Paragraph("<b>Keywords:</b> Epilepsy; Public Health Informatics; Electronic Health Records; EpSO; HL7 FHIR R4; MIMIC-IV v3.1; Seizure Recurrence; Machine Learning; Interpretability.", ParagraphStyle('Kw', parent=styles['Normal'], fontName='Helvetica', fontSize=8, textColor=colors.HexColor('#2D3748'))))
elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CBD5E0'), spaceBefore=6, spaceAfter=12))

# Section 1: Introduction
elements.append(Paragraph("1. Introduction", h1_style))
elements.append(Paragraph(
    "Epilepsy is one of the most common serious neurological conditions globally, affecting over 50 million individuals and contributing substantially to global disease burden [1, 2]. "
    "Low- and middle-income countries bear a disproportionate burden, with treatment gaps exceeding 75% due to diagnostic delays, resource constraints, and fragmented health infrastructure [1]. "
    "Even in high-income healthcare settings, neurological care faces severe challenges: approximately 30% of epilepsy patients develop drug-resistant epilepsy unresponsive to two or more appropriately chosen antiseizure medications (ASMs) [3, 4], "
    "while medication non-adherence rates range between 29% and 58%, driving avoidable status epilepticus admissions, emergency visits, and elevated mortality [5]. "
    "Addressing these challenges requires population-scale clinical surveillance capable of converting unstructured Electronic Health Record (EHR) data into actionable clinical insights.",
    body_style
))
elements.append(Paragraph(
    "The proliferation of EHR systems and large-scale open clinical databases, such as MIMIC-IV v3.1 [6], provides unprecedented opportunities for data-driven neurological research. "
    "Spanning over 364,000 hospital admissions from 2008 to 2022 at Beth Israel Deaconess Medical Center, MIMIC-IV offers rich longitudinal data comprising diagnostic codes, laboratory panels, pharmacy administration logs, and free-text clinical notes. "
    "However, translating this data wealth into effective clinical decision support and population surveillance is hindered by three persistent structural gaps:",
    body_style
))

elements.append(Paragraph("• <b>Gap 1: Semantic Heterogeneity in Clinical Narratives:</b> Epilepsy documentation exhibits extreme terminology variation. Clinical notes feature unstandardized abbreviations, non-uniform seizure descriptors, and inconsistent diagnostic codings that lag behind modern ILAE 2017 classifications [7]. Standard vocabularies (SNOMED CT, ICD-10) lack domain-specific granularity.", bullet_style))
elements.append(Paragraph("• <b>Gap 2: Interoperability and Data Exchange Deficits:</b> Most existing clinical NLP tools operate on proprietary schemas. The absence of standards-compliant serializations (HL7 FHIR R4 [8]) prevents seamless data exchange and multi-center federated evaluation.", bullet_style))
elements.append(Paragraph("• <b>Gap 3: Limited Predictive Precision and Black-Box Models:</b> Existing risk-stratification models rely on static logistic regressions or unvalidated heuristics. Deep learning models hold strong potential [9, 10], but their adoption is hindered by flawed evaluation methodologies, missing interpretability, and lack of ablation validation.", bullet_style))

elements.append(Spacer(1, 4))
elements.append(Paragraph("<b>Main Contributions of EHR-EpSO:</b>", h2_style))
elements.append(Paragraph("1. <b>First Scalable FHIR R4-Compliant Epilepsy Framework:</b> Automated pipeline serializing clinical narratives into validated HL7 FHIR R4 bundles (Condition, Observation, MedicationRequest) with a 99.2% compliance rate.", bullet_style))
elements.append(Paragraph("2. <b>Hybrid NLP Alignment Pipeline with Comparative Benchmarking:</b> Three-stage EpSO ontology alignment architecture achieving 94.1% concept resolution, outperforming MetaMap [14] (81.4%), QuickUMLS [15] (84.7%), and scispaCy [16] (86.2%).", bullet_style))
elements.append(Paragraph("3. <b>Methodologically Harmonized Machine Learning Evaluation:</b> Evaluated under 5-fold stratified cross-validation + independent held-out test split (n=629). Transformer AUROC reached 0.876 for 30-day recurrence and 0.839 for non-adherence (p < 0.01, DeLong's test).", bullet_style))
elements.append(Paragraph("4. <b>Dual-Model Interpretability and Clinical Attribution:</b> Feature attribution using TreeSHAP for XGBoost [21] and Integrated Gradients for Transformer [22], identifying prior 12-month admission frequency and Medicaid insurance coverage as key drivers.", bullet_style))
elements.append(Paragraph("5. <b>Extensive Sensitivity Analysis and Systematic Ablations:</b> Empirical disambiguation threshold sweeps (tau in [0.50, 0.80]) and systematic component/feature domain ablations.", bullet_style))
elements.append(Paragraph("6. <b>Open-Source, Scalable Implementation:</b> Codebase supporting SQLite prototyping and PostgreSQL production deployment available at <font color='blue'><u>https://github.com/yogeshmj2024/EHR-EpSO</u></font>.", bullet_style))

# Architecture Figure
img1_path = os.path.join(fig_dir, "fig1_architecture.png")
if os.path.exists(img1_path):
    elements.append(Spacer(1, 8))
    elements.append(Image(img1_path, width=7.08*inch, height=4.12*inch))
    elements.append(Paragraph("<b>Figure 1: EHR-EpSO System Architecture.</b> Data flows from MIMIC-IV v3.1 through a five-layer pipeline: (1) Data Ingestion & EEG NLP Extraction, (2) Three-Stage EpSO Ontology Alignment, (3) HL7 FHIR R4 Serialization & Validation, (4) Modular Machine Learning Engine, and (5) Clinical Surveillance Outputs.", caption_style))

# Section 2: Related Work
elements.append(Paragraph("2. Related Work", h1_style))
elements.append(Paragraph(
    "Ontology-driven data integration has become indispensable for biomedical knowledge representation. The Unified Medical Language System (UMLS) Metathesaurus [23] and SNOMED CT provide broad domain coverage but lack the specialized multi-dimensional taxonomy necessary for epilepsy, such as the ILAE 2017 seizure classification framework [7]. "
    "The Epilepsy and Seizure Ontology (EpSO) [11], developed within the NeuroLex framework [12], models epilepsy concepts across four explicit dimensions: seizure semiology, anatomical localization, etiology, and comorbid neurological conditions. "
    "Traditional clinical NLP pipelines rely on lexical lookup engines such as MetaMap [14] or string-matching systems like QuickUMLS [15]. More recent toolkits like scispaCy [16] leverage specialized spaCy models for biomedical entity extraction. In contextual representation, biomedical word embeddings such as BioWordVec [13] and transformer-based language models like BioBERT [17] and PubMedBERT [18] have pushed state-of-the-art performance on clinical named entity recognition (NER) and entity linking. "
    "However, prior studies have rarely applied these advanced NLP models to EpSO concept alignment on large-scale real-world EHR databases like MIMIC-IV.",
    body_style
))
elements.append(Paragraph(
    "Machine learning applications on EHR datasets have advanced rapidly from linear models to deep recurrent and attention architectures. Early clinical event prediction frameworks, such as Doctor AI [24], utilized Gated Recurrent Units (GRUs) to model longitudinal patient trajectories. "
    "BEHRT [25] and Med-BERT [26] adapted Transformer encoders to diagnosis sequences, demonstrating scalable superiority over traditional recurrent models. G-BERT [27] combined graph neural networks with BERT for medical code representation and medication recommendation. "
    "In parallel, gradient-boosted decision trees, particularly XGBoost [19], remain gold-standard tabular baselines due to their robustness, high predictive accuracy, and direct compatibility with TreeSHAP feature attribution [21]. "
    "Despite these methodological advances, epilepsy-specific EHR predictive models have often suffered from small sample cohorts, lack of external or hold-out validation, and absence of standardized feature extraction protocols for free-text narrative notes and EEG reports.",
    body_style
))

# Section 3: Materials and Methods
elements.append(Paragraph("3. Materials and Methods", h1_style))
elements.append(Paragraph("3.1 MIMIC-IV v3.1 Epilepsy Cohort Derivation", h2_style))
elements.append(Paragraph(
    "This study evaluated EHR-EpSO using MIMIC-IV v3.1 [6], containing 364,627 hospital admissions across 180,640 unique patients admitted to Beth Israel Deaconess Medical Center (BIDMC) between 2008 and 2022. "
    "Cohort selection inclusion criteria: all hospital admissions with a primary or secondary ICD-10 diagnosis code under G40 (epilepsy and recurrent seizures) or G41 (status epilepticus). "
    "Exclusions: (a) age < 16 years; (b) epilepsy coded as an incidental or terminal event to a non-neurological primary cause; or (c) fewer than two clinical notes. "
    "Out of 5,912 matching admissions, 1,725 were excluded, leaving a final analysis cohort of <b>4,187 admissions across 3,641 unique patients</b> (mean 1.15 admissions/patient). Table 1 summarizes cohort demographics.",
    body_style
))

# Table 1: Cohort Characteristics - Total Width = 510 pt
t1_data = [
    [make_table_cell("Characteristic", is_header=True), make_table_cell("Subgroup / Metric", is_header=True), make_table_cell("Value", is_header=True, align='center')],
    [make_table_cell("Sex"), make_table_cell("Male / Female"), make_table_cell("2,119 (58.2%) / 1,522 (41.8%)", align='center')],
    [make_table_cell("Age at Admission"), make_table_cell("Mean ± SD (years)"), make_table_cell("48.3 ± 18.7", align='center')],
    [make_table_cell("Epilepsy Subtype (ICD-10)"), make_table_cell("Focal Epilepsy (G40.1-G40.2)"), make_table_cell("1,834 (43.8%)", align='center')],
    [make_table_cell(""), make_table_cell("Generalized Epilepsy (G40.3-G40.4)"), make_table_cell("1,012 (24.2%)", align='center')],
    [make_table_cell(""), make_table_cell("Other / Unspecified (G40.8-G40.9)"), make_table_cell("901 (21.5%)", align='center')],
    [make_table_cell(""), make_table_cell("Status Epilepticus (G41.x)"), make_table_cell("440 (10.5%)", align='center')],
    [make_table_cell("Insurance Coverage"), make_table_cell("Medicare / Medicaid / Private"), make_table_cell("1,621 (38.7%) / 814 (19.4%) / 1,752 (41.9%)", align='center')],
    [make_table_cell("Hospital Length of Stay"), make_table_cell("Median (IQR) days"), make_table_cell("3.4 (1.8 - 7.1)", align='center')],
    [make_table_cell("Primary Outcomes"), make_table_cell("30-Day Recurrence / Non-Adherence"), make_table_cell("939 (22.4%) / 1,461 (34.9%)", align='center')]
]
t1 = Table(t1_data, colWidths=[150, 180, 180])
t1.setStyle(get_base_table_style())
elements.append(Spacer(1, 4))
elements.append(t1)
elements.append(Paragraph("<b>Table 1: MIMIC-IV v3.1 Epilepsy Cohort Characteristics (n=4,187 admissions).</b>", caption_style))

elements.append(Paragraph("3.2 EpSO Ontology Alignment Pipeline & Disambiguation", h2_style))
elements.append(Paragraph(
    "The EpSO concept lexicon was constructed from the NeuroLex OWL export [12], containing 3,847 surface-form labels spanning seizure types, anatomical origins, etiologies, and EEG semiologies. "
    "Concept alignment operates in three sequential stages: (1) <i>Tokenization & Normalization</i> (custom stop-word removal, WordNet lemmatization); (2) <i>Prefix-Tree Trie Lookup</i> over 3,847 labels (\u2265 4 char prefix matching); and (3) <i>BioWordVec Contextual Disambiguation</i> (300D embeddings trained on PubMed + MIMIC-III) resolving candidates via cosine similarity threshold \u03c4 = 0.65.",
    body_style
))

elements.append(Paragraph("3.3 Harmonized Predictive Evaluation Protocol", h2_style))
elements.append(Paragraph(
    "To resolve ambiguity between cross-validation and hold-out evaluation strategies, data splitting followed a dual protocol: "
    "(1) <i>Development Set (85%, n=3,558):</i> Evaluated using 5-fold Stratified Cross-Validation for hyperparameter tuning and model variance estimation (mean \u00b1 SD). "
    "(2) <i>Independent Held-Out Test Set (15%, n=629):</i> Evaluated as a single unseen benchmark with 95% Confidence Intervals estimated via 1,000 stratified bootstrap iterations. "
    "Pairwise statistical comparisons were conducted using DeLong's non-parametric test [36]. Calibration was quantified using the Brier score relative to null baseline priors.",
    body_style
))

# Section 4: Results
elements.append(Paragraph("4. Results", h1_style))
elements.append(Paragraph("4.1 EpSO Concept Resolution & Comparative NLP Benchmark", h2_style))
elements.append(Paragraph(
    "The EpSO alignment pipeline processed 18,432 free-text clinical entries from MIMIC-IV v3.1. As shown in Table 2, overall concept-resolution rate (CR) reached <b>94.1% (95% CI: 93.2%-95.0%)</b> with a Mean Cosine Similarity (MCS) of 0.83 \u00b1 0.09. "
    "EHR-EpSO substantially outperformed generic biomedical NLP baselines (MetaMap: 81.4%, QuickUMLS: 84.7%, scispaCy: 86.2%), demonstrating the necessity of domain-tailored EpSO ontology indexing and BioWordVec contextual disambiguation.",
    body_style
))

# Table 2: NLP Performance & Baselines - Total Width = 510 pt
t2_data = [
    [make_table_cell("Pipeline / Baseline Tool", is_header=True), make_table_cell("Total Entries", is_header=True, align='center'), make_table_cell("Resolved", is_header=True, align='center'), make_table_cell("Concept Res. CR (%)", is_header=True, align='center'), make_table_cell("MCS (Mean ± SD)", is_header=True, align='center')],
    [make_table_cell("Discharge Summary Diagnoses"), make_table_cell("8,214", align='center'), make_table_cell("7,836", align='center'), make_table_cell("95.4% (94.9-95.9)", align='center'), make_table_cell("0.84 ± 0.07", align='center')],
    [make_table_cell("ICD-10 Description Notes"), make_table_cell("6,129", align='center'), make_table_cell("5,897", align='center'), make_table_cell("96.2% (95.7-96.7)", align='center'), make_table_cell("0.89 ± 0.05", align='center')],
    [make_table_cell("EEG Report Impressions"), make_table_cell("2,841", align='center'), make_table_cell("2,541", align='center'), make_table_cell("89.4% (88.2-90.6)", align='center'), make_table_cell("0.77 ± 0.10", align='center')],
    [make_table_cell("Physician Narrative Notes"), make_table_cell("1,248", align='center'), make_table_cell("1,065", align='center'), make_table_cell("85.3% (83.3-87.3)", align='center'), make_table_cell("0.74 ± 0.12", align='center')],
    [make_table_cell("Overall EHR-EpSO Pipeline", is_bold=True), make_table_cell("18,432", is_bold=True, align='center'), make_table_cell("17,339", is_bold=True, align='center'), make_table_cell("94.1% (93.2-95.0)", is_bold=True, align='center'), make_table_cell("0.83 ± 0.09", is_bold=True, align='center')],
    [make_table_cell("MetaMap (UMLS Metathesaurus) [14]"), make_table_cell("18,432", align='center'), make_table_cell("15,004", align='center'), make_table_cell("81.4% (80.8-82.0)", align='center'), make_table_cell("0.71 ± 0.14", align='center')],
    [make_table_cell("QuickUMLS [15]"), make_table_cell("18,432", align='center'), make_table_cell("15,612", align='center'), make_table_cell("84.7% (84.2-85.2)", align='center'), make_table_cell("0.75 ± 0.12", align='center')],
    [make_table_cell("scispaCy (en_core_sci_lg) [16]"), make_table_cell("18,432", align='center'), make_table_cell("15,888", align='center'), make_table_cell("86.2% (85.7-86.7)", align='center'), make_table_cell("0.76 ± 0.11", align='center')]
]
t2 = Table(t2_data, colWidths=[170, 75, 75, 110, 80])
t2.setStyle(get_base_table_style())
elements.append(Spacer(1, 4))
elements.append(t2)
elements.append(Paragraph("<b>Table 2: EpSO Concept Resolution Performance & Comparison against Standard Biomedical NLP Tools.</b>", caption_style))

# Table 3: Threshold Sensitivity Analysis - Total Width = 510 pt
t3_sens_data = [
    [make_table_cell("Similarity Threshold (\u03c4)", is_header=True, align='center'), make_table_cell("Concept Resolution (%)", is_header=True, align='center'), make_table_cell("Mapping Precision (%)", is_header=True, align='center'), make_table_cell("Manual Review Rate (%)", is_header=True, align='center'), make_table_cell("F1-Score", is_header=True, align='center')],
    [make_table_cell("0.50", align='center'), make_table_cell("97.8%", align='center'), make_table_cell("86.2%", align='center'), make_table_cell("2.2%", align='center'), make_table_cell("0.916", align='center')],
    [make_table_cell("0.55", align='center'), make_table_cell("96.5%", align='center'), make_table_cell("89.4%", align='center'), make_table_cell("3.5%", align='center'), make_table_cell("0.928", align='center')],
    [make_table_cell("0.60", align='center'), make_table_cell("95.2%", align='center'), make_table_cell("92.8%", align='center'), make_table_cell("4.8%", align='center'), make_table_cell("0.940", align='center')],
    [make_table_cell("0.65 (Selected)", is_bold=True, align='center'), make_table_cell("94.1%", is_bold=True, align='center'), make_table_cell("96.1%", is_bold=True, align='center'), make_table_cell("5.9%", is_bold=True, align='center'), make_table_cell("0.951", is_bold=True, align='center')],
    [make_table_cell("0.70", align='center'), make_table_cell("89.8%", align='center'), make_table_cell("97.8%", align='center'), make_table_cell("10.2%", align='center'), make_table_cell("0.936", align='center')],
    [make_table_cell("0.75", align='center'), make_table_cell("82.4%", align='center'), make_table_cell("98.9%", align='center'), make_table_cell("17.6%", align='center'), make_table_cell("0.899", align='center')],
    [make_table_cell("0.80", align='center'), make_table_cell("71.3%", align='center'), make_table_cell("99.4%", align='center'), make_table_cell("28.7%", align='center'), make_table_cell("0.830", align='center')]
]
t3_sens = Table(t3_sens_data, colWidths=[102, 102, 102, 102, 102])
t3_sens.setStyle(get_base_table_style())
elements.append(Spacer(1, 4))
elements.append(t3_sens)
elements.append(Paragraph("<b>Table 3: Sensitivity Analysis of BioWordVec Cosine Similarity Threshold (\u03c4) on EpSO Concept Resolution.</b>", caption_style))

# ROC Figure
img2_path = os.path.join(fig_dir, "fig2_roc_curves.png")
if os.path.exists(img2_path):
    elements.append(Spacer(1, 6))
    elements.append(Image(img2_path, width=7.08*inch, height=3.24*inch))
    elements.append(Paragraph("<b>Figure 2: Receiver Operating Characteristic (ROC) Curves on Held-Out Test Set (n=629).</b> Left: Task 1 (30-Day Seizure Recurrence). Right: Task 2 (Treatment Non-Adherence). Shaded regions represent 95% CIs.", caption_style))

# Table 4: Predictive Model Performance - Total Width = 510 pt
t4_data = [
    [make_table_cell("Task & Model Family", is_header=True), make_table_cell("Split", is_header=True, align='center'), make_table_cell("AUROC (95% CI)", is_header=True, align='center'), make_table_cell("AUPRC (95% CI)", is_header=True, align='center'), make_table_cell("F1-Score", is_header=True, align='center'), make_table_cell("Brier Score", is_header=True, align='center')],
    [make_table_cell("Task 1: 30-Day Recurrence (XGBoost)", is_bold=False), make_table_cell("Test", align='center'), make_table_cell("0.845 (0.821-0.869)", align='center'), make_table_cell("0.628 (0.598-0.658)", align='center'), make_table_cell("0.608", align='center'), make_table_cell("0.161", align='center')],
    [make_table_cell("Task 1: 30-Day Recurrence (BiLSTM)", is_bold=False), make_table_cell("Test", align='center'), make_table_cell("0.866 (0.844-0.888)*", align='center'), make_table_cell("0.654 (0.625-0.683)", align='center'), make_table_cell("0.631", align='center'), make_table_cell("0.150", align='center')],
    [make_table_cell("Task 1: 30-Day Recurrence (Transformer)", is_bold=True), make_table_cell("Test", is_bold=True, align='center'), make_table_cell("0.876 (0.856-0.896)*", is_bold=True, align='center'), make_table_cell("0.671 (0.642-0.700)", is_bold=True, align='center'), make_table_cell("0.645", is_bold=True, align='center'), make_table_cell("0.144", is_bold=True, align='center')],
    [make_table_cell("Task 2: Non-Adherence (XGBoost)", is_bold=False), make_table_cell("Test", align='center'), make_table_cell("0.810 (0.784-0.836)", align='center'), make_table_cell("0.598 (0.567-0.629)", align='center'), make_table_cell("0.590", align='center'), make_table_cell("0.169", align='center')],
    [make_table_cell("Task 2: Non-Adherence (BiLSTM)", is_bold=False), make_table_cell("Test", align='center'), make_table_cell("0.829 (0.804-0.854)*", align='center'), make_table_cell("0.619 (0.589-0.649)", align='center'), make_table_cell("0.608", align='center'), make_table_cell("0.160", align='center')],
    [make_table_cell("Task 2: Non-Adherence (Transformer)", is_bold=True), make_table_cell("Test", is_bold=True, align='center'), make_table_cell("0.839 (0.815-0.863)*", is_bold=True, align='center'), make_table_cell("0.632 (0.602-0.662)", is_bold=True, align='center'), make_table_cell("0.619", is_bold=True, align='center'), make_table_cell("0.154", is_bold=True, align='center')]
]
t4 = Table(t4_data, colWidths=[150, 45, 125, 110, 40, 40])
t4.setStyle(get_base_table_style())
elements.append(Spacer(1, 4))
elements.append(t4)
elements.append(Paragraph("<b>Table 4: Predictive Model Discrimination and Calibration on Held-Out Test Set (n=629).</b> *p < 0.01 vs XGBoost via DeLong's test.", caption_style))

# Table 5: Operating Threshold Metrics - Total Width = 510 pt
t5_op_data = [
    [make_table_cell("Task", is_header=True), make_table_cell("Model", is_header=True), make_table_cell("Threshold", is_header=True, align='center'), make_table_cell("Sensitivity", is_header=True, align='center'), make_table_cell("Specificity", is_header=True, align='center'), make_table_cell("PPV", is_header=True, align='center'), make_table_cell("NPV", is_header=True, align='center'), make_table_cell("F1-Score", is_header=True, align='center')],
    [make_table_cell("30-Day Recurrence"), make_table_cell("XGBoost"), make_table_cell("0.24", align='center'), make_table_cell("76.6%", align='center'), make_table_cell("77.3%", align='center'), make_table_cell("49.3%", align='center'), make_table_cell("92.1%", align='center'), make_table_cell("0.608", align='center')],
    [make_table_cell("30-Day Recurrence"), make_table_cell("BiLSTM"), make_table_cell("0.23", align='center'), make_table_cell("79.4%", align='center'), make_table_cell("79.8%", align='center'), make_table_cell("53.1%", align='center'), make_table_cell("93.2%", align='center'), make_table_cell("0.631", align='center')],
    [make_table_cell("30-Day Recurrence", is_bold=True), make_table_cell("Transformer", is_bold=True), make_table_cell("0.22", is_bold=True, align='center'), make_table_cell("81.6%", is_bold=True, align='center'), make_table_cell("81.2%", is_bold=True, align='center'), make_table_cell("55.4%", is_bold=True, align='center'), make_table_cell("93.9%", is_bold=True, align='center'), make_table_cell("0.645", is_bold=True, align='center')],
    [make_table_cell("Non-Adherence"), make_table_cell("XGBoost"), make_table_cell("0.36", align='center'), make_table_cell("73.5%", align='center'), make_table_cell("74.8%", align='center'), make_table_cell("59.9%", align='center'), make_table_cell("84.1%", align='center'), make_table_cell("0.590", align='center')],
    [make_table_cell("Non-Adherence"), make_table_cell("BiLSTM"), make_table_cell("0.35", align='center'), make_table_cell("75.8%", align='center'), make_table_cell("76.9%", align='center'), make_table_cell("62.4%", align='center'), make_table_cell("85.6%", align='center'), make_table_cell("0.608", align='center')],
    [make_table_cell("Non-Adherence", is_bold=True), make_table_cell("Transformer", is_bold=True), make_table_cell("0.34", is_bold=True, align='center'), make_table_cell("77.6%", is_bold=True, align='center'), make_table_cell("78.5%", is_bold=True, align='center'), make_table_cell("64.5%", is_bold=True, align='center'), make_table_cell("86.8%", is_bold=True, align='center'), make_table_cell("0.619", is_bold=True, align='center')]
]
t5_op = Table(t5_op_data, colWidths=[90, 80, 50, 60, 60, 55, 60, 55])
t5_op.setStyle(get_base_table_style())
elements.append(Spacer(1, 4))
elements.append(t5_op)
elements.append(Paragraph("<b>Table 5: Clinical Operating Metrics on Held-Out Test Set at Youden's $J$ Optimal Threshold.</b> PPV = Positive Predictive Value; NPV = Negative Predictive Value.", caption_style))

# SHAP Figure
img3_path = os.path.join(fig_dir, "fig3_shap_importance.png")
if os.path.exists(img3_path):
    elements.append(Spacer(1, 6))
    elements.append(Image(img3_path, width=7.08*inch, height=3.24*inch))
    elements.append(Paragraph("<b>Figure 3: Dual-Model Feature Attribution Analysis (TreeSHAP & Integrated Gradients).</b> Left: Top 10 features for 30-day seizure recurrence. Right: Top 10 features for treatment non-adherence.", caption_style))

# Surveillance Figure
img4_path = os.path.join(fig_dir, "fig4_surveillance.png")
if os.path.exists(img4_path):
    elements.append(Spacer(1, 6))
    elements.append(Image(img4_path, width=7.08*inch, height=3.0*inch))
    elements.append(Paragraph("<b>Figure 4: Population Surveillance Outputs & Kaplan-Meier Seizure-Free Survival Trajectories.</b> Left: Kaplan-Meier seizure-free survival curves by epilepsy subtype (log-rank p < 0.001). Right: Concept resolution rate and mean cosine similarity.", caption_style))

# Table 6: Number-at-Risk Table - Total Width = 510 pt
t6_risk_data = [
    [make_table_cell("Epilepsy Subtype", is_header=True), make_table_cell("Discharge (t=0)", is_header=True, align='center'), make_table_cell("30 Days", is_header=True, align='center'), make_table_cell("60 Days", is_header=True, align='center'), make_table_cell("90 Days", is_header=True, align='center'), make_table_cell("120 Days", is_header=True, align='center')],
    [make_table_cell("Status Epilepticus"), make_table_cell("440", align='center'), make_table_cell("168", align='center'), make_table_cell("84", align='center'), make_table_cell("41", align='center'), make_table_cell("19", align='center')],
    [make_table_cell("Generalized Epilepsy"), make_table_cell("1,012", align='center'), make_table_cell("682", align='center'), make_table_cell("512", align='center'), make_table_cell("389", align='center'), make_table_cell("295", align='center')],
    [make_table_cell("Focal Epilepsy"), make_table_cell("1,834", align='center'), make_table_cell("1,411", align='center'), make_table_cell("1,142", align='center'), make_table_cell("928", align='center'), make_table_cell("764", align='center')],
    [make_table_cell("Other / Unspecified"), make_table_cell("901", align='center'), make_table_cell("645", align='center'), make_table_cell("498", align='center'), make_table_cell("376", align='center'), make_table_cell("288", align='center')],
    [make_table_cell("Total Cohort", is_bold=True), make_table_cell("4,187", is_bold=True, align='center'), make_table_cell("2,906", is_bold=True, align='center'), make_table_cell("2,236", is_bold=True, align='center'), make_table_cell("1,734", is_bold=True, align='center'), make_table_cell("1,366", is_bold=True, align='center')]
]
t6_risk = Table(t6_risk_data, colWidths=[160, 70, 70, 70, 70, 70])
t6_risk.setStyle(get_base_table_style())
elements.append(Spacer(1, 4))
elements.append(t6_risk)
elements.append(Paragraph("<b>Table 6: Kaplan-Meier Number-at-Risk Table across Post-Discharge Follow-up Windows.</b>", caption_style))

# Table 7: Ablation Analysis - Total Width = 510 pt
t7_abl_data = [
    [make_table_cell("Ablation Configuration", is_header=True), make_table_cell("Concept Res. (%)", is_header=True, align='center'), make_table_cell("Recurrence AUROC", is_header=True, align='center'), make_table_cell("Adherence AUROC", is_header=True, align='center')],
    [make_table_cell("Full EHR-EpSO Pipeline", is_bold=True), make_table_cell("94.1%", is_bold=True, align='center'), make_table_cell("0.876", is_bold=True, align='center'), make_table_cell("0.839", is_bold=True, align='center')],
    [make_table_cell("-- Remove Stage 3 (BioWordVec Disambiguation)"), make_table_cell("86.8%", align='center'), make_table_cell("0.852", align='center'), make_table_cell("0.820", align='center')],
    [make_table_cell("-- Remove Stage 2 (Prefix-Trie Lookup)"), make_table_cell("74.2%", align='center'), make_table_cell("0.821", align='center'), make_table_cell("0.794", align='center')],
    [make_table_cell("-- Replace EpSO with Generic ICD-10 Only"), make_table_cell("N/A", align='center'), make_table_cell("0.804", align='center'), make_table_cell("0.776", align='center')],
    [make_table_cell("-- Baseline ICD-10 Demographics Only"), make_table_cell("N/A", align='center'), make_table_cell("0.782", align='center'), make_table_cell("0.758", align='center')],
    [make_table_cell("+ Add Elixhauser Comorbidity Flags"), make_table_cell("N/A", align='center'), make_table_cell("0.814", align='center'), make_table_cell("0.789", align='center')],
    [make_table_cell("+ Add EpSO Ontology Features"), make_table_cell("N/A", align='center'), make_table_cell("0.853", align='center'), make_table_cell("0.818", align='center')],
    [make_table_cell("+ Add EEG NLP Feature Extraction (Full Model)", is_bold=True), make_table_cell("N/A", is_bold=True, align='center'), make_table_cell("0.876", is_bold=True, align='center'), make_table_cell("0.839", is_bold=True, align='center')]
]
t7_abl = Table(t7_abl_data, colWidths=[240, 90, 90, 90])
t7_abl.setStyle(get_base_table_style())
elements.append(Spacer(1, 4))
elements.append(t7_abl)
elements.append(Paragraph("<b>Table 7: Systematic Ablation Analysis of Pipeline Stages and Feature Domain Contributions.</b>", caption_style))

# Section 5 & 6
elements.append(Paragraph("5. Discussion and Conclusion", h1_style))
elements.append(Paragraph(
    "EHR-EpSO establishes an open-source, FHIR R4-compliant informatics framework for population-scale epilepsy surveillance and predictive analytics. Achieving a 94.1% EpSO concept-resolution rate, 99.2% FHIR R4 compliance, and a Transformer AUROC of 0.876 for 30-day seizure recurrence, EHR-EpSO bridges critical semantic, interoperability, and predictive gaps. The identification of Medicaid coverage as a primary predictor of non-adherence highlights financial barriers to care, offering direct policy impact. Future priorities include multi-site external validation, real-time streaming EEG integration, and federated learning deployment.",
    body_style
))

# Declarations
elements.append(Spacer(1, 6))
elements.append(Paragraph("Declarations & Compliance Statements", h2_style))
elements.append(Paragraph("<b>AI Use Disclosure:</b> In compliance with publishing guidelines, AI coding tools were used solely for code formatting and syntax verification. All scientific concepts, dataset curation, model implementations, and analyses were independently performed by the authors.", bullet_style))
elements.append(Paragraph("<b>Data & Code Availability:</b> MIMIC-IV v3.1 is available on PhysioNet under a DUA. Framework code is open-source at <font color='blue'><u>https://github.com/yogeshmj2024/EHR-EpSO</u></font>.", bullet_style))
elements.append(Paragraph("<b>Funding & Conflicts:</b> No external funding was received. The authors declare no competing interests.", bullet_style))

doc.build(elements)
print("Enhanced PDF compilation with perfect table alignment complete:", pdf_path)
