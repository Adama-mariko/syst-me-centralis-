import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

export interface ConfirmDialogData {
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  confirmColor?: 'primary' | 'accent' | 'warn';
}

@Component({
  selector: 'app-confirm-dialog',
  standalone: true,
  imports: [
    CommonModule,
    MatDialogModule,
    MatButtonModule,
    MatIconModule
  ],
  template: `
    <div class="confirm-dialog">
      <h2 mat-dialog-title class="dialog-title">
        <mat-icon class="title-icon">help_outline</mat-icon>
        {{ data.title }}
      </h2>
      
      <mat-dialog-content class="dialog-content">
        <p>{{ data.message }}</p>
      </mat-dialog-content>
      
      <mat-dialog-actions class="dialog-actions">
        <button mat-button 
                (click)="onCancel()" 
                class="cancel-btn">
          {{ data.cancelText || 'Annuler' }}
        </button>
        <button mat-raised-button 
                [color]="data.confirmColor || 'warn'"
                (click)="onConfirm()" 
                class="confirm-btn">
          {{ data.confirmText || 'Confirmer' }}
        </button>
      </mat-dialog-actions>
    </div>
  `,
  styles: [`
    .confirm-dialog {
      min-width: 300px;
    }
    
    .dialog-title {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 16px;
    }
    
    .title-icon {
      color: #ff9800;
    }
    
    .dialog-content {
      margin-bottom: 16px;
    }
    
    .dialog-content p {
      margin: 0;
      color: rgba(0, 0, 0, 0.7);
      line-height: 1.5;
    }
    
    .dialog-actions {
      display: flex;
      justify-content: flex-end;
      gap: 8px;
      margin-top: 16px;
    }
    
    .cancel-btn {
      color: rgba(0, 0, 0, 0.6);
    }
    
    .confirm-btn {
      min-width: 100px;
    }
  `]
})
export class ConfirmDialogComponent {
  constructor(
    public dialogRef: MatDialogRef<ConfirmDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: ConfirmDialogData
  ) {}

  onCancel(): void {
    this.dialogRef.close(false);
  }

  onConfirm(): void {
    this.dialogRef.close(true);
  }
}