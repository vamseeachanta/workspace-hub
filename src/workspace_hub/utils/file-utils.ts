/**
 * File system utilities for baseline tracking engine
 */

import * as fs from 'fs-extra';
import * as path from 'path';
import { FileSystemError } from '../types';

export class FileUtils {
  /**
   * Ensures a directory exists, creating it if necessary
   */
  static async ensureDirectory(dirPath: string): Promise<void> {
    try {
      await fs.ensureDir(dirPath);
    } catch (error) {
      throw new FileSystemError(
        `Failed to create directory: ${dirPath}`,
        { originalError: error }
      );
    }
  }

  /**
   * Safely reads a JSON file
   */
  static async readJsonFile<T>(filePath: string): Promise<T> {
    try {
      const content = await fs.readFile(filePath, 'utf-8');
      return JSON.parse(content) as T;
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
        throw new FileSystemError(`File not found: ${filePath}`);
      }
      throw new FileSystemError(
        `Failed to read JSON file: ${filePath}`,
        { originalError: error }
      );
    }
  }

  /**
   * Safely writes a JSON file
   */
  static async writeJsonFile(filePath: string, data: unknown): Promise<void> {
    try {
      await this.ensureDirectory(path.dirname(filePath));
      await fs.writeFile(filePath, JSON.stringify(data, null, 2), 'utf-8');
    } catch (error) {
      throw new FileSystemError(
        `Failed to write JSON file: ${filePath}`,
        { originalError: error }
      );
    }
  }

  /**
   * Checks if a file exists
   */
  static async fileExists(filePath: string): Promise<boolean> {
    try {
      await fs.access(filePath);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Lists files in a directory with optional pattern matching
   */
  static async listFiles(
    dirPath: string,
    pattern?: RegExp
  ): Promise<string[]> {
    try {
      const files = await fs.readdir(dirPath);
      if (pattern) {
        return files.filter(file => pattern.test(file));
      }
      return files;
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
        return [];
      }
      throw new FileSystemError(
        `Failed to list files in directory: ${dirPath}`,
        { originalError: error }
      );
    }
  }

  /**
   * Gets file statistics
   */
  static async getFileStats(filePath: string): Promise<fs.Stats> {
    try {
      return await fs.stat(filePath);
    } catch (error) {
      throw new FileSystemError(
        `Failed to get file stats: ${filePath}`,
        { originalError: error }
      );
    }
  }

  /**
   * Copies a file to a new location
   */
  static async copyFile(source: string, destination: string): Promise<void> {
    try {
      await this.ensureDirectory(path.dirname(destination));
      await fs.copy(source, destination);
    } catch (error) {
      throw new FileSystemError(
        `Failed to copy file from ${source} to ${destination}`,
        { originalError: error }
      );
    }
  }

  /**
   * Deletes a file if it exists
   */
  static async deleteFile(filePath: string): Promise<void> {
    try {
      await fs.remove(filePath);
    } catch (error) {
      throw new FileSystemError(
        `Failed to delete file: ${filePath}`,
        { originalError: error }
      );
    }
  }

  /**
   * Creates a backup of a file with timestamp
   */
  static async createBackup(filePath: string, backupDir?: string): Promise<string> {
    try {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const fileName = path.basename(filePath);
      const backupFileName = `${fileName}.backup.${timestamp}`;

      const backupPath = backupDir
        ? path.join(backupDir, backupFileName)
        : path.join(path.dirname(filePath), backupFileName);

      await this.copyFile(filePath, backupPath);
      return backupPath;
    } catch (error) {
      throw new FileSystemError(
        `Failed to create backup for file: ${filePath}`,
        { originalError: error }
      );
    }
  }

  /**
   * Cleans up old backup files based on retention policy
   */
  static async cleanupBackups(
    backupDir: string,
    pattern: RegExp,
    retentionDays: number
  ): Promise<number> {
    try {
      const files = await this.listFiles(backupDir, pattern);
      const cutoffDate = new Date();
      cutoffDate.setDate(cutoffDate.getDate() - retentionDays);

      let deletedCount = 0;
      for (const file of files) {
      if (!file) continue;
        const filePath = path.join(backupDir, file);
        const stats = await this.getFileStats(filePath);

        if (stats.mtime < cutoffDate) {
          await this.deleteFile(filePath);
          deletedCount++;
        }
      }

      return deletedCount;
    } catch (error) {
      throw new FileSystemError(
        `Failed to cleanup backups in directory: ${backupDir}`,
        { originalError: error }
      );
    }
  }

  /**
   * Creates a secure temporary directory
   */
  static async createTempDirectory(prefix: string = 'baseline-'): Promise<string> {
    try {
      const tempDir = await fs.mkdtemp(path.join(require('os').tmpdir(), prefix));
      return tempDir;
    } catch (error) {
      throw new FileSystemError(
        'Failed to create temporary directory',
        { originalError: error }
      );
    }
  }
}