 # Development Phase Plan (PHASE.md)

## Project Overview
- **Goal**: Python CustomTkinter-based checklist desktop app for users aged 60–70  
- **Core Features**: Dynamic UI generation from `checklist.json` + HWP file integration  
- **User Characteristics**: Requires large fonts, clear buttons, and simple flow  

---

## 📋 Phase 1: Project Setup and Data Structure Implementation

### 1.1 Development Environment Setup
- [x] Set up Python virtual environment
- [x] Install CustomTkinter and required packages
- [x] Design project folder structure
- [x] Initialize Git  

### 1.2 Data Parsing and Structuring
- [x] Implement `checklist.json` parser
  - [x] JSON load and validation function
  - [x] Node classification by type (`title1` → `title2` → `section`)
  - [x] Tree builder function for hierarchy
- [x] Design data model classes
  - [x] Base class `ChecklistNode`
  - [x] Subclasses: `Title1`, `Title2`, `Section`
- [x] Basic state management system
  - [x] Mechanism to save/load checkbox states
  - [x] Progress calculation logic  

---

## 📱 Phase 2: First Screen and Basic UI Layout

### 2.1 First Screen (Initialization)
- [x] Company name input field (large font)
- [x] HWP file upload feature
  - [x] File selection dialog
  - [x] File validation (hwp extension)
  - [x] Display upload status
- [x] [확인] button → Navigate to checklist screen  

### 2.2 Main Window Layout
- [x] Define overall window size and minimum size
- [x] Define left sidebar area
- [x] Define right main content area
- [x] Define bottom navigation area
- [x] Implement responsive layout (handle window resizing)  

---

## 🎯 Phase 3: Sidebar Implementation

### 3.1 Dynamic Sidebar Generation
- [x] Render `title1` items as buttons
- [x] Display company name + "3차 보고서" at the top
- [x] Highlight currently selected `title1`

### 3.2 Sidebar Navigation
- [x] Handle `title1` button click events
- [x] Context switch logic for main page
- [x] Visual feedback for selection (background, border)

### 3.3 Senior-Friendly UI
- [x] Enlarge button size (minimum height 60px)
- [x] Increase font size (minimum 16pt)
- [x] Apply high-contrast colors  

---

## 📊 Phase 4: Main Page – Header and Stepper

### 4.1 Main Page Header
- [ ] Display current `title1.label` as a large title  
- [ ] Show progress (steps completed vs total)  

### 4.2 Stepper UI
- [ ] Display `title2` children of the current `title1` as steps  
- [ ] Format: Step number + label (e.g., "1. 위험성평가 사전준비")  
- [ ] Show checkmark (✓) for completed steps  
- [ ] Highlight current step  

### 4.3 Stepper Navigation
- [ ] On click, move to the selected `title2` section  
- [ ] Implement scroll/page transition animation  
- [ ] Auto-save current state before moving  

---

## ✅ Phase 5: Checklist Area Implementation

### 5.1 Section-wise Checklist Rendering
- [ ] Display all `section` under the selected `title2`  
- [ ] Show `section.label` as subsection headers  
- [ ] Render `items` as checkbox lists  

### 5.2 Checkbox Interaction
- [ ] Individual check/uncheck functionality  
- [ ] Save state immediately upon changes  
- [ ] Provide visual feedback based on status  

### 5.3 Bulk Select Feature
- [ ] Add "Select/Deselect All" button for each section  
- [ ] Large button size for easy touch interaction  
- [ ] Show current selection state  

### 5.4 Completion Tracking
- [ ] Calculate completion rate for each section  
- [ ] Check completion conditions for `title2` steps  
- [ ] Update stepper UI to reflect completion  

---

## 🧭 Phase 6: Navigation System

### 6.1 Bottom Navigation Buttons
- [ ] Implement [이전] [다음] buttons  
- [ ] Enable sequential navigation across `title2` steps  
- [ ] Disable buttons at first/last step accordingly  

### 6.2 Navigation Logic
- [ ] Track current step  
- [ ] Save state on page transitions  
- [ ] Move to Final Review Page after completing the last step  

---

## 📄 Phase 7: Final Review Page

### 7.1 Hierarchical Summary
- [ ] Display all checked items in original hierarchy  
- [ ] Order: `title1` → `title2` → `section` → checked `items`  
- [ ] Use indentation and bullet points for readability  

### 7.2 HWP Conversion Button
- [ ] Place [HWP 변환] button at the bottom  
- [ ] Define external function call interface  
- [ ] Implement placeholder (exclude actual conversion)  

### 7.3 Error Handling
- [ ] Notify user if conversion fails  
- [ ] Validate required fields  
- [ ] Display error messages in large font/high contrast  

---

## 💾 Phase 8: State Saving and Restoration

### 8.1 Session State Management
- [ ] Save checkbox states in JSON/SQLite  
- [ ] Restore state on app restart  
- [ ] Store separately by company/file  

### 8.2 Progress Tracking
- [ ] Calculate and save overall progress  
- [ ] Track step completion status  
- [ ] Optimize auto-save timing  

---

## 🎨 Phase 9: Accessibility and UX Improvements

### 9.1 Senior-Friendly UI
- [ ] Font size option (default ≥ 16pt)  
- [ ] Apply high-contrast color theme  
- [ ] Enlarge touch target size (≥ 44px)  

### 9.2 Keyboard Navigation
- [ ] Tab navigation between elements  
- [ ] Enter/Space keys for checkbox interaction  
- [ ] Arrow keys for step navigation  

### 9.3 Windows DPI Scaling Support
- [ ] Handle high-resolution displays  
- [ ] Auto-detect system DPI  
- [ ] Proportional resizing  

---

## 🐛 Phase 10: Testing and Quality Assurance

### 10.1 Functional Testing
- [ ] Test all checklist scenarios  
- [ ] Test state saving/restoration  
- [ ] Test file upload and conversion  

### 10.2 Usability Testing
- [ ] User testing with 60–70 age group (if possible)  
- [ ] Verify compliance with accessibility guidelines  
- [ ] Validate error handling scenarios  

### 10.3 Performance Optimization
- [ ] Optimize large checklist loading performance  
- [ ] Improve UI responsiveness  
- [ ] Optimize memory usage  

---

## 📦 Phase 11: Deployment and Packaging

### 11.1 Executable Creation
- [ ] Generate exe file using PyInstaller  
- [ ] Validate included dependencies  
- [ ] Set icon and metadata  

### 11.2 Distribution Package
- [ ] Write user manual (large fonts, include screenshots)  
- [ ] Prepare installation guide  
- [ ] Include sample `checklist.json` file  

---

## ⏱️ Estimated Timeline

| Phase | Estimated Duration | Dependencies |
|-------|--------------------|--------------|
| Phase 1 | 1–2 days | - |
| Phase 2 | 2–3 days | Phase 1 |
| Phase 3 | 1–2 days | Phase 1, 2 |
| Phase 4 | 2–3 days | Phase 1, 2, 3 |
| Phase 5 | 3–4 days | Phase 1, 2, 4 |
| Phase 6 | 1–2 days | Phase 4, 5 |
| Phase 7 | 2–3 days | Phase 5, 6 |
| Phase 8 | 2–3 days | Phase 5 |
| Phase 9 | 2–3 days | All previous phases |
| Phase 10 | 2–3 days | All previous phases |
| Phase 11 | 1–2 days | Phase 10 |

**Total Estimated Duration: 19–32 days (approx. 3–5 weeks)**  

---

## 🚨 Key Risks and Mitigation

1. **CustomTkinter Korean font issues**  
   - Risk: Medium  
   - Mitigation: Bundle font files and configure system fonts  

2. **HWP file compatibility**  
   - Risk: High  
   - Mitigation: Research external libraries and prepare alternatives  

3. **Accessibility requirements**  
   - Risk: Medium  
   - Mitigation: Validate usability early with prototypes  

4. **Windows environment compatibility**  
   - Risk: Medium  
   - Mitigation: Test across different Windows versions  

---

## 📝 Next Steps

1. **Start Phase 1**: Set up development environment and implement data parsing  
2. **Technical Validation**: Test CustomTkinter Korean font support and research HWP libraries  
3. **Prototype Development**: Implement MVP version with core features first  