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

interface AppSettings {
  darkMode: boolean;
  animations: boolean;
  compactSidebar: boolean;
  pushNotifications: boolean;
  emailNotifications: boolean;
  notificationSounds: boolean;
  autoRefresh: boolean;
  itemsPerPage: number;
  language: string;
  autoLogout: boolean;
  sessionDuration: number;
}

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
    MatProgressSpinnerModule
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

  constructor(
    private dialogRef: MatDialogRef<SettingsComponent>,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadSettings();
  }

  private loadSettings(): void {
    // Charger les paramètres depuis le localStorage
    const savedSettings = localStorage.getItem('app-settings');
    if (savedSettings) {
      try {
        this.settings = { ...this.settings, ...JSON.parse(savedSettings) };
        this.originalSettings = { ...this.settings };
      } catch (error) {
        console.error('Erreur lors du chargement des paramètres:', error);
      }
    }
  }

  onSettingChange(key: keyof AppSettings, value: any): void {
    this.settings[key] = value as never;
    
    // Appliquer certains changements immédiatement
    this.applySettingChange(key, value);
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
    const dataStr = JSON.stringify(this.settings, null, 2);
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
          try {
            const importedSettings = JSON.parse(e.target.result);
            this.settings = { ...this.settings, ...importedSettings };
            
            // Appliquer tous les paramètres
            Object.keys(this.settings).forEach(key => {
              this.applySettingChange(key as keyof AppSettings, this.settings[key as keyof AppSettings]);
            });
            
            this.snackBar.open('Paramètres importés avec succès', 'Fermer', {
              duration: 3000,
              panelClass: ['success-snackbar']
            });
          } catch (error) {
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
      // Réinitialiser aux valeurs par défaut
      this.settings = {
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

      // Appliquer tous les paramètres
      Object.keys(this.settings).forEach(key => {
        this.applySettingChange(key as keyof AppSettings, this.settings[key as keyof AppSettings]);
      });

      this.snackBar.open('Paramètres réinitialisés', 'Fermer', {
        duration: 3000,
        panelClass: ['success-snackbar']
      });
    }
  }

  onSave(): void {
    this.isLoading = true;
    
    // Sauvegarder dans le localStorage
    localStorage.setItem('app-settings', JSON.stringify(this.settings));
    
    // Simuler un délai de sauvegarde
    setTimeout(() => {
      this.isLoading = false;
      this.originalSettings = { ...this.settings };
      
      this.snackBar.open('Paramètres sauvegardés', 'Fermer', {
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
      Object.keys(this.originalSettings).forEach(key => {
        this.applySettingChange(key as keyof AppSettings, this.originalSettings[key as keyof AppSettings]);
      });
    }
    
    this.dialogRef.close();
  }
}