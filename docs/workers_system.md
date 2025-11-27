# Worker Management System Architecture

## Overview
A robust task-based worker system for processing anime opening quiz data. The system uses a database-driven task queue to coordinate parallel processing across multiple worker types while maintaining data consistency and providing full auditability.

## Core Components

### Database Tables

**TaskQueue**
- Tracks all work that needs to be performed
- Contains task_type enum (FIND_SOURCES, DOWNLOAD_SOURCE, ANALYZE_TIMING, ASSESS_DIFFICULTY, MONITOR_TORRENT)
- Uses strong foreign keys (song_id, source_id) instead of generic entity references
- Includes status tracking (PENDING, ASSIGNED, COMPLETED, FAILED, CANCELLED)
- Stores attempt_count and max_attempts for retry logic
- Has scheduled_after for delayed execution
- Optional JSON data field for complex task parameters
- Automatic created_at and updated_at timestamps

**TaskAssignment**
- Records which worker is currently processing a task
- Links to TaskQueue via task_id
- Stores worker_instance identifier
- Tracks assigned_at timestamp
- No heartbeats - uses task-based completion tracking

**TaskResult**
- Maintains complete history of all task executions
- Records success/failure status and error messages
- Stores which worker processed the task
- Tracks execution timing (started_at, completed_at)
- Includes error_type classification for retry logic

### Services

**TaskCreator**
- Monitors database for work that needs to be done
- Creates appropriate tasks based on entity states
- Handles task chaining (download completion triggers timing analysis)
- Ensures no duplicate tasks are created
- Runs periodically to find new work

**TaskDispatcher**
- Manages assignment of tasks to workers
- Uses database-level locking (SKIP LOCKED) for parallel safety
- Ensures each task is only assigned to one worker
- Provides tasks to workers based on creation order
- Handles task claiming and assignment

**WorkerSupervisor**
- Monitors system health
- Detects and handles stalled tasks
- Provides system metrics and monitoring
- Can manually reset stuck tasks if needed

### Worker Types

**SourceFindWorker**
- Strategies: AniTousen, Shiki, YouTube
- Processes FIND_SOURCES tasks
- Finds video sources for songs
- Creates DOWNLOAD_SOURCE tasks for found sources

**DownloadWorker**
- Strategies: YtDlp, Local file
- Processes DOWNLOAD_SOURCE tasks
- Downloads videos from various sources
- Updates source status (DOWNLOADING → DOWNLOADED/INVALID)
- For torrents: creates MONITOR_TORRENT task instead of waiting

**TorrentDownloadWorker**
- Specialized download worker for torrents
- Adds torrents to qBittorrent client
- Immediately creates MONITOR_TORRENT task
- Marks DOWNLOAD_SOURCE task as completed (job is to start download)

**TorrentMonitorWorker**
- Processes MONITOR_TORRENT tasks
- Checks torrent progress in qBittorrent
- Reschedules itself if download incomplete
- Updates source status when download completes
- Handles torrent disappearance by recreating download tasks

**TimingWorker**
- Strategies: Default, Random
- Processes ANALYZE_TIMING tasks
- Analyzes downloaded videos for quiz segments
- Creates timing entries with guess_start and reveal_start

**DifficultyWorker**
- Strategies: Random
- Processes ASSESS_DIFFICULTY tasks
- Calculates difficulty levels for songs
- Can run independently of other processing

## Workflow Lifecycle

### Task Creation
- TaskCreator periodically scans database for work
- Songs without sources get FIND_SOURCES tasks
- Sources without local files get DOWNLOAD_SOURCE tasks
- Downloaded sources without timings get ANALYZE_TIMING tasks
- Songs without difficulty assessments get ASSESS_DIFFICULTY tasks
- Automatic task chaining: download completion triggers timing analysis

### Task Assignment
- Workers poll dispatcher for available tasks
- Dispatcher uses SKIP LOCKED to prevent duplicate assignments
- Each task is assigned to exactly one worker
- Assignment is recorded in TaskAssignment table
- Workers receive tasks matching their supported types

### Task Execution
- Worker calls appropriate strategy with entity ID
- Strategy contains business logic (unchanged from original)
- Worker handles database state updates
- All exceptions are caught and classified
- TaskResult record created for each execution attempt

### Completion Handling
- Successful tasks marked COMPLETED
- Failed tasks classified by error type
- Temporary failures rescheduled with exponential backoff
- Permanent failures marked FAILED and not retried
- Task chaining triggers subsequent processing

## Error Handling

### Error Classification
- Temporary failures: network issues, timeouts, external service unavailable
- Permanent failures: invalid sources, corrupt files, unsupported formats
- Classification determines retry behavior

### Retry Logic
- Temporary failures rescheduled with increasing delays
- Maximum attempt count prevents infinite retries
- Failed tasks include detailed error messages for debugging
- Permanent failures require manual intervention if needed

### Crash Recovery
- No heartbeat system - workers either complete or fail
- Crashed workers leave tasks in ASSIGNED state
- Supervisor can detect and reset stuck assignments
- Manual intervention rarely needed due to clear error states

## Special Cases

### Torrent Download Handling
- Two-phase process: DOWNLOAD_SOURCE → MONITOR_TORRENT
- Download worker starts torrent, monitor tracks progress
- Monitor handles torrent disappearance by recreating download task
- External resource management through qBittorrent integration

### Entity Deletion
- Foreign key constraints prevent orphaned records
- Cleanup service handles external resource removal
- Torrents removed from client when sources deleted
- Tasks automatically cancelled when entities deleted

### Concurrent Processing
- Database-level locking prevents race conditions
- SKIP LOCKED allows parallel workers to skip contested tasks
- Each entity processed by only one worker at a time
- System scales horizontally by adding more workers

## System Behavior

### Performance Characteristics
- Database handles worker polling with minimal load
- Task claiming uses efficient indexed queries
- Audit trail provides complete processing history
- JSON data field allows flexible task parameters

### Monitoring and Debugging
- TaskResult table provides complete execution history
- Error messages and classifications aid debugging
- Task status shows current system state
- Supervisor can identify and reset problematic tasks

### Maintenance Considerations
- Periodic cleanup of old TaskResult records may be needed
- Task queue can be monitored for backlog
- Worker logs provide detailed processing information
- Database indexes maintained for optimal performance

## Integration with Existing System

### Worker Strategies
- All existing strategies from hanyuu.txt remain unchanged
- Strategies receive entity IDs instead of complex queries
- Business logic isolated from task management
- Easy to add new strategies and worker types

### Database Schema
- Builds on existing entity relationships
- Strong foreign keys maintain data integrity
- Check constraints enforce domain rules
- Fits naturally with existing anime/song/source model

### API Integration
- Entity deletion triggers task cleanup
- Manual task creation through API possible
- System status visible through task queries
- Workers operate independently of web interface

This architecture provides a robust, scalable foundation for processing anime opening quiz data while maintaining the clean separation of concerns and architectural purity that aligns with the project's goals. The system is designed to be maintainable by a single developer while providing enterprise-grade reliability and observability.
