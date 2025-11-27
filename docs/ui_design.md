# Anime Opening Quiz Factory - UI Design Specification

## Layout Structure

### Three-Column Design
The interface is divided into three fixed-width columns, each containing multiple stacked blocks. Each block has a fixed height that varies across the layout, preventing horizontal alignment between columns.

**Column 1 (Left - Anime Column)**
- **Anime List Block**: Primary navigation for browsing all anime in the database

**Column 2 (Middle - Anime Details & Songs Column)**
- **Anime Details Block**: Detailed view and management for selected anime
- **Anime Infos Block**: Metadata from various sources for selected anime
- **Songs List Block**: All openings/endings for selected anime

**Column 3 (Right - Song Details Column)**
- **Sources Block**: Video sources for selected song
- **Timings Block**: Quiz timing segments for selected source
- **Levels Block**: Difficulty assessments for selected song

## Visual Design System

### Color Coding by Entity Type
Each block type has a subtle background tint (white with 1% color) for visual distinction:
- **Red Tint**: Anime-related blocks (Anime List, Anime Details, Anime Infos)
- **Blue Tint**: Song-related blocks (Songs List)
- **Yellow Tint**: Source-related blocks (Sources)
- **Green Tint**: Level-related blocks (Levels)
- **Purple Tint**: Timing-related blocks (Timings)

### Anime Status Indicator Colors
Anime entity status is shown through prominent background colors:
- **NORMAL**: Default white/light gray (workers can process freely)
- **FINALIZED**: Light blue (workers won't modify songs list, but can process existing songs)
- **BLACKLISTED**: Light gray (workers ignore this anime and all dependent entities completely)

### Source Status Indicator Colors
Source entity status is shown through prominent background colors:
- **NORMAL**: Default white/light gray (awaiting processing)
- **DOWNLOADING**: Light yellow (video download in progress)
- **DOWNLOADED**: Light green (video successfully downloaded and available)
- **INVALID**: Light red (source cannot be processed or downloaded)

## Manual Creation & Deletion System

### Creation Permissions
- **Songs**: Can manually create, edit, and delete any song
- **Sources**: Can manually create with `added_by="manual"`; can only edit/delete if `added_by="manual"`
- **Timings**: Can manually create with `added_by="manual"`; can only edit/delete if `added_by="manual"`
- **Levels**: Can manually create with `added_by="manual"`; can only edit/delete if `added_by="manual"`
- **Animes**: Cannot manually create (worker-only)

### Deletion Indicators
- Delete buttons (trash icons) appear as small icons at the end of list items
- **Songs**: Always show delete button
- **Sources/Timings/Levels**: Only show delete button if `added_by="manual"`

## Block Specifications

### Anime List Block
**Purpose**: Primary navigation and overview of all anime in the system

**Content**:
- List of all anime entries from database
- Each item displays: title, release year, anime status color coding
- Virtual scrolling handles large datasets (1000+ entries)

**User Interactions**:
- Click any anime to select it (updates middle and right columns)
- Use search bar to filter by title in real-time
- Use filter buttons to show: All, Normal, Finalized, or Blacklisted anime
- Use sort dropdown to order by: Alphabetical, Reverse Alphabetical, Newest, Oldest, Recently Added, Recently Updated

### Anime Details Block
**Purpose**: View and manage selected anime properties

**Content**:
- Large poster image
- Anime title and release year
- Current anime status display
- MAL (MyAnimeList) hyperlink

**User Interactions**:
- Status dropdown to change between NORMAL, FINALIZED, BLACKLISTED
- Click MAL link to open external page

### Anime Infos Block
**Purpose**: Display metadata collected from various sources

**Content**:
- List of anime_info entries for selected anime
- Each item shows source name and data summary

**User Interactions**:
- Click to view detailed metadata (could expand or show in modal)

### Songs List Block
**Purpose**: Browse and select openings/endings for current anime

**Content**:
- List of song entries for selected anime
- Each item displays: "OP1 - Artist - Song Title" format with edit pencil icon and delete trash icon
- Inherits anime status color from parent anime
- "Add Song" button above the list

**User Interactions**:
- Click any song to select it (updates right column blocks)
- Click edit pencil icon to modify song details (category, number, artist, title)
- Click delete trash icon to remove song (with confirmation dialog)
- Click "Add Song" button to open song creation popup
- Use sort dropdown to order by: Number (natural OP/ED order), Recently Added, Recently Updated

**Add Song Popup Form**:
- Category dropdown (OP/ED)
- Number input field
- Artist text input
- Song Name text input
- Create and Cancel buttons

### Sources Block
**Purpose**: Manage video sources for selected song

**Content**:
- List of source entries for selected song
- Each item displays: added_by field and source status with delete trash icon (only if added_by="manual")
- Color coding shows source status (Normal, Downloading, Downloaded, Invalid)
- "Add Source" button above the list

**User Interactions**:
- Click any source to select it (updates Timings block)
- Click delete trash icon to remove source (only shown for manual sources, with confirmation)
- Click "Add Source" button to open source creation popup
- Status changes automatically as workers process downloads

**Add Source Popup Form**:
- URL text input field
- Create and Cancel buttons
- Transforms URL input to location={"url":"<user_input>"} in backend

### Timings Block
**Purpose**: View quiz timing segments for selected source

**Content**:
- List of timing entries for selected source
- Each item displays: added_by, guess_start, reveal_start timestamps with delete trash icon (only if added_by="manual")
- "Add Timing" button above the list

**User Interactions**:
- Click delete trash icon to remove timing (only shown for manual timings, with confirmation)
- Click "Add Timing" button to open timing creation popup
- Click to view/edit timing details (only for manual timings)

**Add Timing Popup Form**:
- Guess Start timestamp (float input)
- Reveal Start timestamp (float input)
- Create and Cancel buttons

### Levels Block
**Purpose**: View difficulty assessments for selected song

**Content**:
- List of level entries for selected song
- Each item displays: added_by and difficulty value (0-100) with delete trash icon (only if added_by="manual")
- "Add Level" button above the list

**User Interactions**:
- Click delete trash icon to remove level (only shown for manual levels, with confirmation)
- Click "Add Level" button to open level creation popup
- View-only display of automated difficulty calculations (for worker-added levels)

**Add Level Popup Form**:
- Difficulty value input (0-100 integer)
- Create and Cancel buttons

## Navigation Logic & Data Flow

### Selection Hierarchy
The interface follows a strict parent-child relationship:

1. **Select Anime** → Updates:
   - Anime Details Block (shows selected anime details)
   - Anime Infos Block (shows metadata for selected anime)
   - Songs List Block (shows songs for selected anime)
   - Clears right column blocks (Sources, Timings, Levels)

2. **Select Song** → Updates:
   - Sources Block (shows video sources for selected song)
   - Levels Block (shows difficulty levels for selected song)
   - Clears Timings Block

3. **Select Source** → Updates:
   - Timings Block (shows quiz segments for selected source)

### Empty State Messaging
Each block shows appropriate messages based on context:
- **No Parent Selected**: "Select [parent entity] to view [current entity]"
- **No Data Available**: "No [entities] found for selected [parent entity]"

## Workers Management Page

### Separate Interface
A dedicated page for monitoring and controlling the automation system.

**Content**:
- List of all running workers with current status
- Worker parameters and configuration
- Processing statistics and progress indicators

**User Interactions**:
- Start new workers with configurable strategies and intervals
- Stop running workers
- Monitor worker health and activity logs

## Data Display Standards

### Entity Formatting
- **Anime Items**: "Title (Year)" with anime status color coding
- **Song Items**: "OP/ED + Number - Artist - Song Name" with edit/delete icons (e.g., "OP2 - SPYAIR - Some Like It Hot!!")
- **Source Items**: "added_by" with source status color coding and conditional delete icon
- **Timing Items**: "added_by: guess_start → reveal_start" with conditional delete icon
- **Level Items**: "added_by: value/100" with conditional delete icon

### Performance Considerations
- Virtual scrolling implemented for Anime List to handle large datasets
- Real-time search filtering without page reload
- Efficient data loading with pagination or incremental fetching as needed

## Interaction Patterns

### Visual Feedback
- Selected items highlighted with border or background change
- Hover states for interactive elements
- Loading indicators for data fetching operations
- Status changes reflected immediately through color updates
- Confirmation dialogs for all delete operations

### Control Placement
- Search/filter/sort controls always visible above respective lists
- Action buttons (status changes, add buttons) located in appropriate detail blocks
- Delete/edit icons positioned at the end of list items
- Navigation flows left-to-right following database relationships

### Popup Form Behavior
- All creation forms appear as centered modal popups
- Forms include validation for basic data types (numbers, required fields)
- Successful creation refreshes the relevant block
- Cancel button closes popup without changes
- Forms maintain context (which anime/song/source the new entity belongs to)
