# Phone Library

<div align="center">

**Large-Scale Autonomous Digital Library & Computer-Vision Document Processing Pipeline**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Computer Vision](https://img.shields.io/badge/Computer%20Vision-PyMuPDF%20%7C%20Pillow-ff69b4?style=for-the-badge)](https://pymupdf.readthedocs.io/)
[![Corpus](https://img.shields.io/badge/Corpus-8%2C500%2B%20Volumes-orange?style=for-the-badge)](https://benjelloun.dev/library)
[![Storage](https://img.shields.io/badge/Storage-34%2B%20GB%20Android%20FTP-green?style=for-the-badge&logo=android&logoColor=white)](https://benjelloun.dev/library)
[![Catalog](https://img.shields.io/badge/Reconciliation-Shamela%20%7C%20Waqfeya%20%7C%20Archive-8A2BE2?style=for-the-badge)](https://benjelloun.dev/library)

[**🌐 Live Catalog & Web Index (benjelloun.dev/library)**](https://benjelloun.dev/library)

</div>

---

## 📌 Executive Summary

**Phone Library** is a production-grade autonomous curation and document-processing pipeline designed to manage, verify, normalize, and optimize a massive collection of classical Arabic and Islamic heritage PDF volumes (**8,500+ books, 34+ GB**).

The system solves a unique hardware-architecture challenge: **the primary digital collection lives on an Android smartphone's internal storage**, while all compute-heavy computer vision, OCR analysis, deduplication, catalog cross-referencing, and web indexing run autonomously on a **Linux workstation** communicating with the device over high-speed local FTP.

Every file alteration, rename, crop, or edition upgrade is strictly governed by deterministic batch plans (`plans/NNN-*.tsv`), audited in an append-only transactional log (`data/changes/changes.tsv`), and verified through automated regression suites and browser-based human-in-the-loop review interfaces.

---

## 🏗️ System Architecture & Data Flow

```mermaid
flowchart TB
    subgraph StorageLayer ["📱 Physical Storage Layer (Android Phone)"]
        PhoneStorage["Internal Storage: Books/<category>/<book>/<volume>.pdf\n(Source of Truth: 8,500+ Volumes / 34+ GB)"]
        FTPServer["Android FTP Server (High-Speed Local WiFi Transport)"]
        PhoneStorage <--> FTPServer
    end

    subgraph Transport ["🔌 Secure Transport & Synchronization"]
        SyncEngine["scripts/phone_host.py & local_sync_plan.py\n(Credential Isolation, Chunked Transfer, Retry Loop)"]
        FTPServer <-->|Encrypted / Local Transport| SyncEngine
    end

    subgraph ProcessingCore ["💻 Linux Processing Engine (Workstation)"]
        direction TB

        subgraph IngestionAudit ["1. Verification & Integrity"]
            MagicCheck["check_magic.py & check_pdf_tail.py\n(Corrupted File & EOF Detection)"]
            DedupEngine["dup_check.py & same_scan.py\n(Exact & Perceptual Hash Deduplication)"]
        end

        subgraph CatalogReconciliation ["2. Tri-Corpus Reconciliation"]
            ShamelaDB[("Local Shamela SQLite\n(~/.local/share/shamela/)")]
            WaqfeyaDB[("Waqfeya Database\n(books.jsonl + details.jsonl)")]
            ArchiveAPI[("Internet Archive API\n(items.jsonl + files.jsonl)")]
            
            Compare["compare_shamela.py & compare_waqfeya.py\n(Edition Matching, Missing Volume Detection)"]
            ShamelaDB --> Compare
            WaqfeyaDB --> Compare
            ArchiveAPI --> Compare
        end

        subgraph CVPipeline ["3. Computer Vision Auto-Crop Engine"]
            BookCrop["book_crop.py (200 KB Specialized Heuristics)\n- Two-Page Spread Splitting\n- Dynamic Margin & Gutter Detection\n- Footnote Line & Heading Isolation\n- Skew Correction & Edge Despeckling"]
            CropRegress["crop_regress.py & crop_minitest.py\n(Multi-Century Typographic Regression Suite)"]
            BookCrop --> CropRegress
        end

        subgraph Governance ["4. Planning & Governance Engine"]
            BatchPlans["Deterministic Plans\n(plans/NNN-name.tsv)"]
            ChangeLog[("Transactional Ledger\n(data/changes/changes.tsv)")]
            ReviewServer["review_server.py (Port 8765)\nInteractive Human-in-the-Loop Approval"]
            
            BatchPlans --> ReviewServer
            ReviewServer -->|Approved| ChangeLog
        end
    end

    subgraph Publishing ["🌐 Web & Index Distribution"]
        SiteBuilder["build_site.py\n(Responsive Static Catalog Generator)"]
        WebRepo["kmbenjel/library (GitHub Pages)\nbenjelloun.dev/library"]
        PhoneIndexes["Books/فهارس الويب/\n(Local Offline HTML/JSON Indexes on Phone)"]
        
        ChangeLog --> SiteBuilder
        SiteBuilder --> WebRepo
        SiteBuilder --> PhoneIndexes
    end

    SyncEngine <--> IngestionAudit
    IngestionAudit --> CatalogReconciliation
    CatalogReconciliation --> BatchPlans
    BatchPlans --> CVPipeline
    CVPipeline --> ChangeLog
    ChangeLog --> SyncEngine
```

---

## 🔬 Computer Vision Auto-Crop Pipeline (`book_crop.py`)

Classical Arabic typography presents severe challenges for generic document croppers: varying margins across centuries, non-standard commentary and footnote dividers, dual-column glosses, and irregular scanning gutters.

`scripts/book_crop.py` implements a bespoke multi-stage computer vision algorithm:

```mermaid
stateDiagram-v2
    [*] --> IngestPage: Render Vector/Raster Page (PyMuPDF)
    IngestPage --> AnalyzeSpread: Detect Page Spread Aspect Ratio
    
    state AnalyzeSpread {
        [*] --> SinglePage: Ratio < Threshold
        [*] --> SplitSpread: Ratio >= Threshold (Two-page scan)
        SplitSpread --> SplittingGutter: Locate Spine / Center Crease
        SplittingGutter --> SeparatePages: Yield Left & Right Pages
    }

    AnalyzeSpread --> Binarize: Adaptive Thresholding & Edge Density
    
    state Binarize {
        [*] --> TextDensityMap: Horizontal & Vertical Histograms
        TextDensityMap --> DetectHeader: Filter Running Folio / Section Titles
        TextDensityMap --> DetectFootnote: Locate Horizontal Rules & Tahqiq Separators
        DetectFootnote --> BoundingBox: Calculate Tight Ink Bounding Box
    }

    Binarize --> SafetyPaddings: Apply Golden Ratio Padding & Symmetric Margins
    SafetyPaddings --> RegressionCheck: Test Against Historic Layouts
    RegressionCheck --> OutputPDF: Lossless Stream Write / Non-Destructive Crop
    OutputPDF --> [*]
```

### Key CV Capabilities:
1. **Spread Splitting**: Automatically differentiates between single-page scans and open book two-page spreads, isolating the physical gutter without truncating inward margins.
2. **Footnote & Separator Boundary Detection**: Preserves microscopic diacritics and tiny editorial footnote markers often discarded by conventional white-space trimmers.
3. **Typography-Aware Regression Matrix**: Tested against historical editions ranging from Bulaq (19th c.), Matba'at al-Sa'ada, Dar al-Kutub al-Ilmiyya, Dar al-Ma'arif, to modern academic editions.

---

## 📊 Tri-Corpus Reconciliation Engine

The pipeline guarantees that the collection contains the most complete, verified, and highest-fidelity scan of any book:

```mermaid
flowchart LR
    A["Collection Books (8,500+)"] --> M["Fuzzy Matching & Normalization Engine\n(Arabic Text Normalizer & Hijri Century Math)"]
    
    subgraph Corpora ["Authoritative Corpora"]
        S["Shamela Database\n(Digital Master DB)"]
        W["Waqfeya Catalog\n(Investigator & Publisher Metadata)"]
        IA["Internet Archive\n(High-Res PDF Scans & File Hashes)"]
    end

    S --> M
    W --> M
    IA --> M

    M --> O1["🔍 Identify Missing Volumes in Multi-Volume Sets"]
    M --> O2["⚡ Detect Superior Color / Uncut Editions"]
    M --> O3["🏷️ Standardize Exact Publisher & Investigator Names"]
    M --> O4["🔗 Link Digital Texts to High-Resolution Physical Scans"]
```

---

## 🛡️ Engineering Safeguards & Resource Governance

- **Systemd Resource Governors**: Compute-heavy jobs run under dedicated user units with explicit memory boundaries (`MemoryMax=2.5G`), ensuring background cropping never locks or starves workstation development.
- **Append-Only Transactional Ledger**: Every move, rename, join, or crop records `timestamp`, `action`, `source_path`, `dest_path`, `reason`, and `plan_id` in `data/changes/changes.tsv`.
- **Zero Credential Exposure**: FTP credentials and authentication tokens reside exclusively in local runtime environments outside Git tracking.
- **Human-in-the-Loop Web Gate**: High-impact plan batches generate HTML review pages (`scripts/review_server.py`) with side-by-side thumbnail comparisons before commits are executed.

---

## 📂 Repository Layout

```
phone-library/
├── scripts/
│   ├── book_crop.py         # 200 KB Computer vision cropping engine
│   ├── crop_regress.py      # Automated visual regression test runner
│   ├── compare_shamela.py   # Local Shamela SQLite database cross-referencer
│   ├── compare_waqfeya.py   # Waqfeya metadata & volume completeness checker
│   ├── build_catalog.py     # Unified library catalog compiler
│   ├── build_site.py        # Static responsive web reader and search generator
│   ├── review_server.py     # Local HTTP review server (port 8765)
│   ├── phone_host.py        # Android FTP connectivity and transport socket
│   └── publish_web.sh       # Auto-deployment script for GitHub Pages
├── data/
│   ├── changes/changes.tsv  # Append-only transactional ledger of all actions
│   ├── shamela/             # Shamela master database exports
│   ├── waqfeya/             # Waqfeya JSONL catalogs and volume details
│   └── catalog.json         # Complete compiled library index
├── plans/                   # Historical TSV execution plans (370+ batches)
├── AGENTS.md                # Autonomous AI agent guidelines & domain rules
├── HANDOFF.md               # Continuous state handoff across multi-model sessions
└── README.md                # This documentation
```

---

## 📸 Intelligent Cropping, Web Index & Mobile Reader Showcase

> [!NOTE]
> Below are placeholder slots for visual captures, side-by-side computer-vision crop comparisons, and the live catalog web reader.

<div align="center">

| 📖 Before & After CV Cropping | 🌐 Live Web & Mobile Catalog |
|:---:|:---:|
| ![Crop Comparison Placeholder](https://placehold.co/500x700/1e293b/38bdf8?text=CV+Crop+Before+%26+After) <br> *Intelligent margin trimming & footnote boundary preservation* | ![Web Catalog Placeholder](https://placehold.co/500x700/1e293b/10b981?text=benjelloun.dev/library+Reader) <br> *Fast search, instant filters, and cross-category navigation* |

</div>

<br>

<div align="center">

| 🔍 Interactive Review Interface (Port 8765) | 📱 Android Phone Internal Storage Integration |
|:---:|:---:|
| ![Review Page Placeholder](https://placehold.co/500x700/1e293b/f59e0b?text=Plan+Review+Dashboard) <br> *Visual side-by-side approval dashboard before atomic moves* | ![Mobile Storage Placeholder](https://placehold.co/500x700/1e293b/8b5cf6?text=Android+FTP+File+Sync) <br> *34+ GB organized directly on mobile storage over FTP* |

</div>

---

## 📄 License

Engineered with precision by [Khalid Benjelloun](https://benjelloun.dev). Web index accessible at [benjelloun.dev/library](https://benjelloun.dev/library).
