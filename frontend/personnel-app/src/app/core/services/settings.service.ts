import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export interface AppSettings {
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

@Injectable({
  providedIn: 'root'
})
export class SettingsService {
  private readonly STORAGE_KEY = 'app-settings';
  
  private defaultSettings: AppSettings = {
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

  private settingsSubject = new BehaviorSubject<AppSettings>(this.defaultSettings);
  public settings$ = this.settingsSubject.asObservable();

  constructor() {
    this.loadSettings();
  }

  private loadSettings(): void {
    try {
      const savedSettings = localStorage.getItem(this.STORAGE_KEY);
      if (savedSettings) {
        const settings = { ...this.defaultSettings, ...JSON.parse(savedSettings) };
        this.settingsSubject.next(settings);
        this.applySettings(settings);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des paramètres:', error);
    }
  }

  getSettings(): AppSettings {
    return this.settingsSubject.value;
  }

  updateSettings(newSettings: Partial<AppSettings>): void {
    const currentSettings = this.settingsSubject.value;
    const updatedSettings = { ...currentSettings, ...newSettings };
    
    this.settingsSubject.next(updatedSettings);
    this.saveSettings(updatedSettings);
    this.applySettings(updatedSettings);
  }

  private saveSettings(settings: AppSettings): void {
    try {
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(settings));
    } catch (error) {
      console.error('Erreur lors de la sauvegarde des paramètres:', error);
    }
  }

  private applySettings(settings: AppSettings): void {
    // Appliquer le thème sombre
    if (settings.darkMode) {
      document.body.classList.add('dark-theme');
    } else {
      document.body.classList.remove('dark-theme');
    }

    // Appliquer les animations
    if (!settings.animations) {
      document.body.classList.add('no-animations');
    } else {
      document.body.classList.remove('no-animations');
    }

    // Appliquer la sidebar compacte
    if (settings.compactSidebar) {
      document.body.classList.add('compact-sidebar');
    } else {
      document.body.classList.remove('compact-sidebar');
    }
  }

  resetSettings(): void {
    this.settingsSubject.next(this.defaultSettings);
    this.saveSettings(this.defaultSettings);
    this.applySettings(this.defaultSettings);
  }

  exportSettings(): string {
    return JSON.stringify(this.settingsSubject.value, null, 2);
  }

  importSettings(settingsJson: string): boolean {
    try {
      const importedSettings = JSON.parse(settingsJson);
      const validatedSettings = { ...this.defaultSettings, ...importedSettings };
      
      this.settingsSubject.next(validatedSettings);
      this.saveSettings(validatedSettings);
      this.applySettings(validatedSettings);
      
      return true;
    } catch (error) {
      console.error('Erreur lors de l\'importation des paramètres:', error);
      return false;
    }
  }
}