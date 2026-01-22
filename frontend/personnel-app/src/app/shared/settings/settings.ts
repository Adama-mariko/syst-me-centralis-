import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar } from '@angular/material/snack-bar';
import { SettingsService, AppSettings } from '../../core/services/settings.service';
import { TranslationService } from '../../core/services/translation.service';
import { TranslatePipe } from '../pipes/translate.pipe';

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatSelectModule,
    MatButtonModule,
    MatIconModule,
    MatSlideToggleModule,
    MatProgressSpinnerModule,
    TranslatePipe
  ],
  templateUrl: './settings.html',
  styleUrl: './settings.scss'
})
export class SettingsComponent implements OnInit {
  settings: AppSettings = {
    darkMode: false,
    animations: true,
    compactSidebar: false,
    pushNotifications: true,
    emailNotifications: false,
    notificationSounds: true,
    autoRefresh: true,
    itemsPerPage: 25,
    language: 'fr',
    autoLogout: false,
    sessionDuration: 60
  };

  isLoading = false;
  private originalSettings: AppSettings = { ...this.settings };
  availableLanguages = [
    { code: 'fr', name: 'Français' },
    { code: 'en', name: 'English' },
    { code: 'es', name: 'Español' }
  ];

  constructor(
    private dialogRef: MatDialogRef<SettingsComponent>,
    private snackBar: MatSnackBar,
    private settingsService: SettingsService,
    private translationService: TranslationService
  ) {}

  ngOnInit(): void {
    this.loadSettings();
  }

  private loadSettings(): void {
    // Charger les paramètres depuis le service
    this.settings = { ...this.settingsService.getSettings() };
    this.originalSettings = { ...this.settings };
  }

  onSettingChange(key: keyof AppSettings, value: any): void {
    this.settings[key] = value as never;
    
    // Appliquer le changement immédiatement via le service
    const partialUpdate = { [key]: value } as Partial<AppSettings>;
    this.settingsService.updateSettings(partialUpdate);
  }

  private applySettingChange(key: keyof AppSettings, value: any): void {
    switch (key) {
      case 'darkMode':
        this.toggleDarkMode(value);
        break;
      case 'animations':
        this.toggleAnimations(value);
        break;
      case 'compactSidebar':
        this.toggleCompactSidebar(value);
        break;
      default:
        break;
    }
  }

  private toggleDarkMode(enabled: boolean): void {
    // TODO: Implémenter le thème sombre
    if (enabled) {
      document.body.classList.add('dark-theme');
    } else {
      document.body.classList.remove('dark-theme');
    }
  }

  private toggleAnimations(enabled: boolean): void {
    // TODO: Implémenter la désactivation des animations
    if (enabled) {
      document.body.classList.remove('no-animations');
    } else {
      document.body.classList.add('no-animations');
    }
  }

  private toggleCompactSidebar(enabled: boolean): void {
    // TODO: Implémenter la sidebar compacte
    if (enabled) {
      document.body.classList.add('compact-sidebar');
    } else {
      document.body.classList.remove('compact-sidebar');
    }
  }

  exportSettings(): void {
    const dataStr = this.settingsService.exportSettings();
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(dataBlob);
    link.download = 'personnel-manager-settings.json';
    link.click();
    
    this.snackBar.open('Paramètres exportés avec succès', 'Fermer', {
      duration: 3000,
      panelClass: ['success-snackbar']
    });
  }

  importSettings(): void {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    
    input.onchange = (event: any) => {
      const file = event.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (e: any) => {
          const success = this.settingsService.importSettings(e.target.result);
          
          if (success) {
            // Recharger les paramètres dans le composant
            this.loadSettings();
            
            this.snackBar.open('Paramètres importés avec succès', 'Fermer', {
              duration: 3000,
              panelClass: ['success-snackbar']
            });
          } else {
            this.snackBar.open('Erreur lors de l\'importation', 'Fermer', {
              duration: 3000,
              panelClass: ['error-snackbar']
            });
          }
        };
        reader.readAsText(file);
      }
    };
    
    input.click();
  }

  resetSettings(): void {
    if (confirm('Êtes-vous sûr de vouloir réinitialiser tous les paramètres ?')) {
      this.settingsService.resetSettings();
      this.loadSettings(); // Recharger les paramètres dans le composant

      this.snackBar.open('Paramètres réinitialisés', 'Fermer', {
        duration: 3000,
        panelClass: ['success-snackbar']
      });
    }
  }

  onSave(): void {
    this.isLoading = true;
    
    // Sauvegarder tous les paramètres via le service
    this.settingsService.updateSettings(this.settings);
    
    // Simuler un délai de sauvegarde
    setTimeout(() => {
      this.isLoading = false;
      this.originalSettings = { ...this.settings };
      
      const message = this.translationService.translate('message.settingsSaved');
      this.snackBar.open(message, this.translationService.translate('common.close'), {
        duration: 3000,
        panelClass: ['success-snackbar']
      });
      
      this.dialogRef.close(this.settings);
    }, 500);
  }

  onCancel(): void {
    // Restaurer les paramètres originaux si des changements ont été faits
    const hasChanges = JSON.stringify(this.settings) !== JSON.stringify(this.originalSettings);
    
    if (hasChanges) {
      // Restaurer les paramètres originaux via le service
      this.settingsService.updateSettings(this.originalSettings);
    }
    
    this.dialogRef.close();
  }
}