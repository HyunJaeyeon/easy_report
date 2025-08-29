# AGENT.md

## Project Overview
This project is a **desktop application built with Python + CustomTkinter**.  
The app reads the hierarchy (`type`) information from **`checklist.json`** and automatically constructs the **Sidebar / Main Area**.  
The primary users are **workers in their 60s–70s**, so the design must apply **large fonts, clear buttons, and a simple flow**.  
※ The app UI labels will remain in **Korean**.

---

## Data Schema
`checklist.json` follows the type rules below:

- `title1`: Top-level title (shown in the sidebar as buttons)  
- `title2`: Mid-level title (shown in the stepper UI of the main area)  
- `section`: Subsection group (a group of checklist items)  
- `items`: The actual checklist item array  

Example:
```json
[
  {
    "id": "summary",
    "label": "컨설팅 결과 총평서",
    "type": "title1",
    "children": [
      {
        "id": "mustdo",
        "label": "이것만은 꼭 해주세요!",
        "type": "title2",
        "children": [
          {
            "id": "mgt",
            "label": "경영층",
            "type": "section",
            "items": [
              "위험성평가 준비사항 확인",
              "검토 및 평가계획 수립"
            ]
          }
        ]
      }
    ]
  }
]
```

___

# Screen Layout and Rendering Rules

## 1) Sidebar (Left Sidebar)
- **Display Target**: Only `type: "title1"` is shown  
- **Format**: Show `[Company Name] 3rd Report` as the top title, with `title1.label` listed as buttons below  
- **Action**: Clicking a `title1` button → switches the main page to that `title1` context  

## 2) Main Page (Main Area)
- **Header**: Display the current `title1.label` prominently as the main title  
- **Stepper UI (Step indicator + Navigation)**  
  - **Display Target**: Direct `title2` children of the current `title1`  
  - **Format**: Render as a Stepper (1, 2, 3, …) so the order is clearly visible  
  - **Action**: Clicking a step navigates to that `title2` page (scroll/page switch)  
  - **Completion State**: When all `section.items` under a `title2` are checked, mark the step as complete (✓)  
- **Checklist Area**  
  - **Display Target**: `section` nodes under the selected `title2`  
  - **Format**: Show `section.label` as subsection headers, and `items` as a list of checkboxes  
  - **Interaction**:  
    - Checking/unchecking items immediately saves state (memory/file, to be implemented)  
    - Each section provides a **“Select/Deselect All”** option (for elderly users)  
- **Bottom Navigation**  
  - Provide [Previous] [Next] buttons to move between `title2` steps  
  - When the last `title2` is completed, navigate to the **Final Review Page**  

---

# Flow

1. **First Screen**
   - Enter company name  
   - Upload hwp file  
   - [Confirm] → Enter checklist screen  

2. **Checklist Screen**
   - Left: `title1` list (Sidebar navigation)  
   - Right: `title1` header + `title2` stepper + `section` checklists + [Previous]/[Next]  

3. **Final Review**
   - Display a hierarchical summary of all checked items  
   - Show [HWP Conversion] button  
   - On click: match uploaded hwp file fields with user inputs and convert  
   - ⚠️ Conversion function is provided separately → leave only call placeholder (no implementation)  

---

# HWP Conversion Button
- **Location**: Bottom of the Final Review page  
- **Action**: (External function call) Map inputs → hwp fields and save  
- **Error Handling**: If mapping fails or fields are missing, clearly notify the user (large font/high contrast)  

---

# UX/UI Guidelines (for users aged 60–70)
- Large font size, enlarged button/checkbox touch targets  
- Stepper should show **numbers + labels** (e.g., `1. Risk Assessment Preparation`)  
- Strong emphasis on current and next steps (bold, border, background highlight)  
- Provide **Select/Deselect All** at the section level  
- Clear navigation for going back (when clicking sidebar/stepper, show where it leads)  
- Error/confirmation messages must be **short, clear, and in large text**  

---

# Development Checklist
- [ ] Parse `checklist.json`: build type-based tree (`title1` → `title2` → `section`)  
- [ ] Sidebar: dynamically generate `title1` list and navigation  
- [ ] Main header: reflect current `title1.label`  
- [ ] Stepper: render only `title2` children of current `title1` in order, implement click navigation  
- [ ] Checklist: render each `section` under current `title2` as `label` + `items` checkboxes  
- [ ] Progress saving: store checkbox states (session/file) and mark steps complete  
- [ ] Final Review page: build summary text in original hierarchy (title1 → title2 → section → bullet points)  
- [ ] HWP conversion call: connect to function signature only, leave implementation empty  
- [ ] Handle Korean fonts / Windows DPI scaling support  