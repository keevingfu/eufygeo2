import { Readable } from 'stream';
import csv from 'csv-parser';
import { Pool } from 'pg';
import Bull from 'bull';

// Example CSV import with progress tracking
// Demonstrates:
// 1. Streaming large files
// 2. Batch database operations
// 3. Progress reporting
// 4. Error recovery

interface ImportProgress {
  total: number;
  processed: number;
  errors: Array<{ row: number; error: string }>;
  status: 'processing' | 'completed' | 'failed';
}

export class CSVImporter {
  private db: Pool;
  private importQueue: Bull.Queue;

  constructor(db: Pool) {
    this.db = db;
    this.importQueue = new Bull('csv-import', {
      redis: {
        host: process.env.REDIS_HOST,
        port: parseInt(process.env.REDIS_PORT || '6379')
      }
    });

    this.setupQueueProcessor();
  }

  // Queue processor for background imports
  private setupQueueProcessor() {
    this.importQueue.process(async (job) => {
      const { filePath, userId } = job.data;
      return this.processImport(filePath, userId, job);
    });
  }

  // Main import function with streaming
  async importKeywords(
    fileStream: Readable,
    userId: number,
    onProgress?: (progress: ImportProgress) => void
  ): Promise<ImportProgress> {
    const progress: ImportProgress = {
      total: 0,
      processed: 0,
      errors: [],
      status: 'processing'
    };

    const batch: any[] = [];
    const batchSize = 100;
    let rowNumber = 0;

    return new Promise((resolve, reject) => {
      fileStream
        .pipe(csv())
        .on('data', async (row) => {
          rowNumber++;
          
          try {
            // Validate and transform row
            const keyword = this.transformRow(row);
            batch.push(keyword);

            // Process batch when full
            if (batch.length >= batchSize) {
              fileStream.pause();
              await this.processBatch(batch.splice(0, batchSize), progress);
              
              if (onProgress) {
                onProgress({ ...progress });
              }
              
              fileStream.resume();
            }
          } catch (error: any) {
            progress.errors.push({ row: rowNumber, error: error.message });
          }
          
          progress.total = rowNumber;
        })
        .on('end', async () => {
          // Process remaining batch
          if (batch.length > 0) {
            await this.processBatch(batch, progress);
          }
          
          progress.status = progress.errors.length > 0 ? 'completed' : 'completed';
          resolve(progress);
        })
        .on('error', (error) => {
          progress.status = 'failed';
          reject(error);
        });
    });
  }

  // Transform CSV row to keyword object
  private transformRow(row: any) {
    return {
      keyword: row.keyword || row.query || row.term,
      search_volume: parseInt(row.search_volume || row.volume || '0'),
      difficulty: parseFloat(row.difficulty || row.kd || '0'),
      cpc: parseFloat(row.cpc || '0'),
      priority_tier: this.calculatePriorityTier(row),
      metadata: {
        source: row.source || 'csv_import',
        imported_at: new Date()
      }
    };
  }

  // Calculate priority tier based on volume
  private calculatePriorityTier(row: any): string {
    const volume = parseInt(row.search_volume || row.volume || '0');
    if (volume >= 30000) return 'P0';
    if (volume >= 20000) return 'P1';
    if (volume >= 15000) return 'P2';
    if (volume >= 10000) return 'P3';
    return 'P4';
  }

  // Process batch with transaction
  private async processBatch(
    keywords: any[],
    progress: ImportProgress
  ): Promise<void> {
    const client = await this.db.connect();
    
    try {
      await client.query('BEGIN');

      // Bulk insert with conflict handling
      const query = `
        INSERT INTO keywords (
          keyword, search_volume, difficulty, cpc, priority_tier, metadata
        ) VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (keyword) DO UPDATE SET
          search_volume = EXCLUDED.search_volume,
          difficulty = EXCLUDED.difficulty,
          cpc = EXCLUDED.cpc,
          priority_tier = EXCLUDED.priority_tier,
          metadata = keywords.metadata || EXCLUDED.metadata,
          updated_at = NOW()
        RETURNING id
      `;

      for (const keyword of keywords) {
        try {
          await client.query(query, [
            keyword.keyword,
            keyword.search_volume,
            keyword.difficulty,
            keyword.cpc,
            keyword.priority_tier,
            keyword.metadata
          ]);
          progress.processed++;
        } catch (error: any) {
          progress.errors.push({
            row: progress.processed + 1,
            error: error.message
          });
        }
      }

      await client.query('COMMIT');
    } catch (error) {
      await client.query('ROLLBACK');
      throw error;
    } finally {
      client.release();
    }
  }

  // Queue import job for background processing
  async queueImport(filePath: string, userId: number): Promise<Bull.Job> {
    return this.importQueue.add({
      filePath,
      userId,
      timestamp: new Date()
    }, {
      attempts: 3,
      backoff: {
        type: 'exponential',
        delay: 5000
      }
    });
  }

  // Get import job status
  async getImportStatus(jobId: string): Promise<any> {
    const job = await this.importQueue.getJob(jobId);
    if (!job) return null;

    return {
      id: job.id,
      status: await job.getState(),
      progress: job.progress(),
      result: job.returnvalue,
      error: job.failedReason
    };
  }
}