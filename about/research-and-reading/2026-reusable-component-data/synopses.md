---
published: false
---

# A Reusable Component Data Model for Documenting Building Components in Circular Construction Platforms

## Source

- Slug: `2026-reusable-component-data`
- Authors: Gonçal Costa, Adirane Calvo, Álvaro Sicilia, Markel Comenzana, Pau Campos, Roc Jansà, Daniel Sánchez, Albert Mestre and Alejandro Cifuentes.
- Publication: Circular Economy and Sustainability, volume 6, article 471.
- Published: 11 November 2026.
- DOI: https://doi.org/10.1007/s43615-026-01184-8
- Original full text: https://link.springer.com/article/10.1007/s43615-026-01184-8
- Accessed: 16 November 2026. Publisher HTML full text accessible; DOI resolver initially failed, but direct publisher access succeeded. Supplementary dataset not independently inspected.
- Licence: [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/). These notes paraphrase and selectively discuss the paper; they do not reproduce its figures or tables.
- Supporting research materials identified by the paper: https://doi.org/10.5281/zenodo.22029993 (version 1.0.0).

## Synopsis

The study develops a method for deriving reusable building-component information requirements when existing-building records are incomplete. Its focus is the selection and organisation of useful, obtainable information, rather than a universal exhaustive parameter list. A common structure is complemented by requirements applicable to particular component categories.

The five stages are initial parameter identification, assessment against the BAMB reference framework, component applicability and mapping, professional review and refinement, and operationalisation with empirical evaluation. Initial requirements were informed by components and documentation from Barcelona's Abaceria Central Market and practitioner contributions. Building Legacy implements the resulting structure through component-specific templates and individual records.

Availability assesses practical obtainability; Eligibility assesses contextual relevance. Their combined selection rules classify candidate BAMB parameters as core, relevant, complementary or excluded. Selection is separate from applicability to a component category and from mapping into the resulting model. Correspondence can be exact or related, and mappings can combine or separate parameters. This is not simply a subset of BAMB.

## Main arguments and findings

- The resulting model includes 66 common parameters, complemented by component-specific requirements, and was applied across six component categories.
- Parameter coverage for the analysed components was approximately 53–63%. Coverage measures the presence of values, not their accuracy or fitness for reuse.
- Building Legacy generates individual data-entry templates with mandatory and optional requirements. Mandatory information is necessary for valid marketplace publication; these requirements are independent of the derivation-stage Availability/Eligibility classification. All six analysed components met the mandatory requirements, while unavailable optional fields remained empty.
- The workflow combines Revit-based extraction, manual information from documentation and inspections, and separately associated supporting documents. Extracted values agreed with the corresponding supplied case-study information. This tests retrieval and transfer, not the truth of the original source.
- The paper distinguishes model-level requirements from records of how those requirements were derived. Parameter derivation provenance is not itself information that each physical component record must repeat.
- Component records can accumulate later ownership, refurbishment and transport information. Missing earlier history is not assumed to have been reconstructed.
- Technical suitability for a particular reuse application remains a professional assessment, rather than an automated platform verdict.

## Qualifications and limitations

The six categories helped develop the model and then served in its application: they are not an independent validation dataset. The professional review refined the resulting data sheets, rather than independently validating the selection method. Scoring was discussed among researchers rather than independently scored by multiple raters.

The empirical scope is one building. Coverage is specific to the supplied component records, not an estimate for all members of those categories. Acquisition was demonstrated in Revit using one BIM model; broader openBIM/IFC exchange remains future work. The study addresses individual components; extension to assemblies and building systems needs further investigation.

The paper identifies provenance, heterogeneous sources and uncertainty as challenges. It does not establish that availability or coverage certifies the reliability of a value. It does not investigate ExoSett, endorse its architecture or validate its engineering. Do not attribute ExoSett's identification-standard choices to these authors.

## Relevance to ExoSett

The following is **ExoSett's interpretation**, based on the actual 2.0.0 prototype rather than the older architecture's outstanding-work list.

Reviewed modelling repository commit: `f816e9f0cd97e745b03fd8690896148b1968c5bc` (clean checkout at review). Website base commit: `68d8d2fea0f61ba18773bbe00667dee35828522a`.

Reviewed `docs/information-model.md`, `docs/format-2.0.0.md`, `docs/information-model-standards.md`, `docs/prototype-2.0.0-findings.md`, the common/class/building/component schemas, publication-set schema and repair/inspection examples. Public documentation links pin the reviewed modelling commit.

### Existing capabilities

- Building Class Documents contain reusable component definitions; there is no fourth principal component-class document category. Interfaces and detailed requirements belong conceptually here, but the implemented vocabulary is limited to descriptions, dimensions, dependencies, positions and illustrative constraints.
- Component Instance Documents preserve physical identity (`scheme`, `issuer`, `value`), an exact class reference, state, condition and assessment. A class reference is distinct from an assertion of conformity.
- Building Instance Documents adopt a class revision and distinguish position identity from occupant identity. Accepted publication sets reconcile physical deployment against their baseline. Class dependencies resolve separately; publication sets are supporting coordination records.
- Inspection-only component revisions need not force building revisions. Building assignment references can preserve the revision used as installation evidence while later component snapshots remain consistent with that deployment.
- Metadata already records author, recorded/effective/observed times, previous revision, change, evidence and correction. Evidence already references an external artifact with subject and role. Integrity checking does not authenticate the source or establish engineering suitability.
- Explicit unknown deployment, occupancy and effective time are supported. Prepared publication sets and accepted sets have different consistency implications.

### Gaps and possible subsequent work — no model changes in this task

1. **Property-level information states.** `condition` is required nonempty text. Explicit unknowns in selected fields do not supply a general distinction among unknown, unavailable and not applicable. Consider a narrowly scoped property/evidence profile before adding a generic extensibility mechanism.
2. **Assertion-level provenance.** Evidence subjects address a whole revision or an existing ID. The current component fields have no individual property IDs or standard source/method/uncertainty representation. Explore how measurements and inferred assertions would point to evidence; avoid reducing reliability to one confidence number.
3. **Evidence lifecycle and authority.** External artifacts are already available, so do not propose introducing evidence links as though absent. Clarify issuer, scope, observation method, validity and withdrawal handling where a real use case needs them. Current validation does not establish signature, authority or continuing validity.
4. **Stage-specific acceptance.** Assessment statuses and evidence requirements are a foundation, not an encoded inspection or recertification regime. Define minimum evidence for actual lifecycle decisions with practitioners, distinguishing marketplace publication from structural reinstallation.
5. **Engineering detail.** Nominal dimensions and illustrative span constraints are not a comprehensive material, tolerance, condition or performance model. Develop a small real component example before deciding which facts require structured core fields and which can remain referenced evidence.
6. **Revision policy.** Coordination and intermediate snapshots are already implemented. Further work should clarify when new condition evidence changes a building's accepted assessment and how unchanged final locations retain removal/repair history. Do not introduce an unnecessary cascade of building revisions for every inspection.

Identity should continue to preserve external schemes and issuing context. The reviewed standards mapping considers ISO/IEC 15459-4, ISO/IEC 8506 and ISO 81346-12 in distinct roles, with no claim of implemented standards conformance or a new ExoSett serial scheme.

## Points reflected on the website

The public discussion uses one beam's changing deployment to explain class, physical item and building position. It distinguishes existing evidence/unknown-state capabilities from remaining questions, explains immutable assertions and coordinated publication, and closes with four grouped design questions. It links the original paper, the reviewed ExoSett architecture/format/standards documents and the related demountable-connections and design-for-disassembly discussions.

The article and index entry describe 2.0.0 as a working prototype. They do not imply a stable engineering standard, a complete lifecycle application, independent validation of the research model, or validation of ExoSett by Costa and colleagues.
