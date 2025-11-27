# Worker Management System Architecture

## Overview

A sophisticated task-based worker system designed for processing anime opening quiz data. This system replaces the previous file-based worker coordination with a robust database-driven approach that provides full auditability, parallel execution, and automatic error recovery while maintaining clean architectural boundaries.

## Core Database Schema

The system introduces three new tables that integrate with the existing anime/song/source data model.

The TaskQueue table serves as the central work registry. It uses strong foreign key relationships instead of generic entity references - each task type is constrained to reference the appropriate entity type. FIND_SOURCES and ASSESS_DIFFICULTY tasks reference songs, while DOWNLOAD_SOURCE, ANALYZE_TIMING, and MONITOR_TORRENT tasks reference sources. This design ensures database-level integrity through check constraints.

Each task tracks its current status through a state machine: PENDING when created, ASSIGNED when claimed by a worker, then transitioning to COMPLETED, FAILED, or CANCELLED. The system maintains attempt counts with configurable maximum retry limits. A scheduled_after field enables delayed execution for retry scenarios, while a JSON data field stores parameters for complex operations like torrent monitoring.

The TaskAssignment table provides real-time visibility into currently executing work. Each assignment links a task to a specific worker instance, recording when the assignment occurred. Crucially, this table does not use heartbeats - workers either complete tasks successfully or fail with exceptions, eliminating the need for continuous status updates during long-running operations.

The TaskResult table maintains a complete historical record of all execution attempts. Each result records the worker instance, execution timing, outcome status, and detailed error information when failures occur. This audit trail enables comprehensive debugging and system monitoring.

## System Services Architecture

The TaskCreator service acts as the work identification engine. It periodically scans the database to detect processing opportunities - songs needing sources, sources awaiting download, downloaded sources requiring timing analysis, and songs without difficulty assessments. It creates appropriate tasks with automatic chaining: download completion triggers timing analysis, source discovery triggers download tasks. The service ensures no duplicate tasks are created for the same work.

The TaskDispatcher manages the distribution of work to available workers. It uses PostgreSQL's SKIP LOCKED feature to safely coordinate parallel worker access, ensuring each task is assigned to exactly one worker. Workers request work by specifying the task types they support, and the dispatcher provides the oldest eligible task based on creation timestamp.

The WorkerSupervisor provides system health monitoring and maintenance. It can identify tasks that may be stuck and provides mechanisms for manual intervention when necessary. This service also handles system-wide cleanup operations.

## Worker Implementation Details

SourceFindWorker implementations search for video sources using various strategies. The AniTousen strategy parses torrent contents to match anime titles and opening sequences. The Shiki strategy examines Shikimori video attachments for relevant content. The YouTube strategy performs search queries and scores results based on title matching and metadata analysis. Successful source discovery automatically creates corresponding download tasks.

DownloadWorker handles immediate file acquisition. The YtDlp strategy downloads videos from various online platforms with format selection and progress tracking. The Local strategy validates existing file paths and ensures video file integrity. Both strategies update source status throughout the download process and handle platform-specific error conditions.

TorrentDownloadWorker specializes in torrent-based acquisition. Instead of waiting for completion, this worker adds torrents to the qBittorrent client with proper file prioritization then immediately creates a corresponding MONITOR_TORRENT task. This two-phase approach separates torrent initiation from progress tracking.

TorrentMonitorWorker manages long-running torrent downloads. It periodically checks torrent progress in qBittorrent, updating the task schedule while downloads continue. Upon completion, it updates the source record with the local file path. If a torrent disappears from the client, the worker can recreate the original download task to restart the process.

TimingWorker analyzes downloaded videos to identify optimal quiz segments. Strategies examine audio patterns, visual changes, and structural elements to determine guess_start and reveal_start timestamps that create engaging quiz experiences.

DifficultyWorker assesses song challenge levels using various heuristics. These assessments can run independently of other processing stages and contribute to the overall quiz difficulty balancing.

## Workflow Execution Lifecycle

Task creation begins when the TaskCreator identifies unprocessed entities. For new songs, it creates simultaneous FIND_SOURCES and ASSESS_DIFFICULTY tasks. When sources are found, DOWNLOAD_SOURCE tasks are generated. Successful downloads trigger ANALYZE_TIMING tasks. The system maintains these dependencies through database state rather than explicit task relationships.

Worker coordination follows a precise claiming protocol. Workers periodically poll the dispatcher, which uses database transactions with row-level locking to ensure exclusive task assignment. The SKIP LOCKED clause allows multiple workers to concurrently request work without blocking each other on contested tasks.

Task execution encapsulates the business logic within strategy patterns. Workers invoke strategies with the appropriate entity IDs, maintaining separation between coordination logic and domain processing. All exceptions are caught, classified, and handled according to established error policies.

Completion processing varies by outcome. Successful executions mark tasks complete and may trigger subsequent processing chains. Failed executions are analyzed to determine retry eligibility - temporary failures like network issues are rescheduled with exponential backoff, while permanent failures like invalid sources are marked as unrecoverable.

## Error Handling and Recovery System

Error classification forms the foundation of the recovery system. Temporary failures include network timeouts, external service unavailability, and resource contention - these are automatically retried. Permanent failures encompass invalid URLs, unsupported formats, and corrupt files - these require manual intervention after maximum retry attempts.

The retry mechanism implements exponential backoff with jitter. First retry occurs after 5 minutes, then 10, then 20, up to the configured maximum attempts. This approach balances quick recovery with system load management. Each retry increments the attempt counter and updates the scheduled_after timestamp.

Crash recovery leverages the database's transactional consistency. Since workers don't use heartbeats, a crashed worker leaves its task in the ASSIGNED state. The WorkerSupervisor can detect these situations by looking for assignments without recent completion, allowing for manual reset when necessary.

For torrent-specific scenarios, the system implements self-healing behavior. If a torrent disappears from the client, the monitor worker can recreate the original download task. If entity deletion occurs during processing, cleanup services remove external resources and cancel associated tasks.

## Special Case Handling

The torrent download process uses a sophisticated two-phase approach. The DOWNLOAD_SOURCE task handles client integration and initial configuration, while the MONITOR_TORRENT task manages progress tracking. This separation allows the system to handle hours-long downloads without blocking worker resources or requiring complex progress reporting.

Entity deletion triggers comprehensive cleanup cascades. When songs or sources are deleted, the system identifies all related tasks and ensures external resources are properly released. Torrents are removed from the client, and any in-progress processing is gracefully terminated.

Concurrent processing is managed through database-level isolation. The SKIP LOCKED pattern allows multiple workers to operate simultaneously without coordination overhead, while foreign key constraints and check constraints maintain data integrity across parallel operations.

## System Integration and Operation

Worker strategies from the previous implementation remain completely unchanged. The existing business logic for source finding, download handling, timing analysis, and difficulty assessment integrates seamlessly with the new task coordination layer. Strategies receive entity IDs and focus purely on domain processing.

The web interface gains comprehensive monitoring capabilities. Administrators can view task backlogs, execution history, error rates, and system throughput. Manual task creation and management operations are available for special scenarios and debugging.

Performance characteristics are designed for operational efficiency. Database queries use appropriate indexes for fast task selection. The polling interval balances responsiveness with system load. The audit trail provides detailed insights for performance optimization and capacity planning.

Maintenance considerations include periodic archiving of historical task results and monitoring of queue growth patterns. The system provides built-in visibility into processing bottlenecks and error trends, enabling proactive management.

This architecture represents a significant evolution from the previous file-based approach, providing enterprise-grade reliability while maintaining the clean separation of concerns and architectural purity that aligns with the project's core values. The system is specifically designed for long-term maintainability by a single developer while handling the complex coordination requirements of media processing workflows.
