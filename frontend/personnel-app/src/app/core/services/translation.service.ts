import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

interface Translations {
  [key: string]: {
    [language: string]: string;
  };
}

@Injectable({
  providedIn: 'root'
})
export class TranslationService {
  private currentLanguageSubject = new BehaviorSubject<string>('fr');
  public currentLanguage$ = this.currentLanguageSubject.asObservable();

  private translations: Translations = {
    // Navigation
    'nav.dashboard': {
      'fr': 'Tableau de bord',
      'en': 'Dashboard',
      'es': 'Panel de control'
    },
    'nav.users': {
      'fr': 'Utilisateurs',
      'en': 'Users',
      'es': 'Usuarios'
    },
    'nav.companies': {
      'fr': 'Entreprises',
      'en': 'Companies',
      'es': 'Empresas'
    },
    'nav.employees': {
      'fr': 'Collaborateurs',
      'en': 'Employees',
      'es': 'Empleados'
    },
    'nav.placements': {
      'fr': 'Placements',
      'en': 'Placements',
      'es': 'Colocaciones'
    },
    'nav.replacements': {
      'fr': 'Remplacements',
      'en': 'Replacements',
      'es': 'Reemplazos'
    },
    'nav.traceability': {
      'fr': 'Traçabilité',
      'en': 'Traceability',
      'es': 'Trazabilidad'
    },
    'nav.logout': {
      'fr': 'Déconnexion',
      'en': 'Logout',
      'es': 'Cerrar sesión'
    },

    // Common
    'common.save': {
      'fr': 'Sauvegarder',
      'en': 'Save',
      'es': 'Guardar'
    },
    'common.cancel': {
      'fr': 'Annuler',
      'en': 'Cancel',
      'es': 'Cancelar'
    },
    'common.close': {
      'fr': 'Fermer',
      'en': 'Close',
      'es': 'Cerrar'
    },
    'common.edit': {
      'fr': 'Modifier',
      'en': 'Edit',
      'es': 'Editar'
    },
    'common.delete': {
      'fr': 'Supprimer',
      'en': 'Delete',
      'es': 'Eliminar'
    },
    'common.add': {
      'fr': 'Ajouter',
      'en': 'Add',
      'es': 'Agregar'
    },

    // Settings
    'settings.title': {
      'fr': 'Paramètres',
      'en': 'Settings',
      'es': 'Configuración'
    },
    'settings.display': {
      'fr': 'Affichage',
      'en': 'Display',
      'es': 'Pantalla'
    },
    'settings.notifications': {
      'fr': 'Notifications',
      'en': 'Notifications',
      'es': 'Notificaciones'
    },
    'settings.dashboard': {
      'fr': 'Tableau de bord',
      'en': 'Dashboard',
      'es': 'Panel de control'
    },
    'settings.security': {
      'fr': 'Sécurité',
      'en': 'Security',
      'es': 'Seguridad'
    },
    'settings.language': {
      'fr': 'Langue',
      'en': 'Language',
      'es': 'Idioma'
    },
    'settings.darkMode': {
      'fr': 'Thème sombre',
      'en': 'Dark theme',
      'es': 'Tema oscuro'
    },
    'settings.animations': {
      'fr': 'Animations',
      'en': 'Animations',
      'es': 'Animaciones'
    },
    'settings.compactSidebar': {
      'fr': 'Sidebar compacte',
      'en': 'Compact sidebar',
      'es': 'Barra lateral compacta'
    },

    // Messages
    'message.settingsSaved': {
      'fr': 'Paramètres sauvegardés avec succès',
      'en': 'Settings saved successfully',
      'es': 'Configuración guardada exitosamente'
    },
    'message.settingsReset': {
      'fr': 'Paramètres réinitialisés',
      'en': 'Settings reset',
      'es': 'Configuración restablecida'
    }
  };

  constructor() {
    // Charger la langue sauvegardée
    const savedLanguage = localStorage.getItem('app-language');
    if (savedLanguage && this.isValidLanguage(savedLanguage)) {
      this.setLanguage(savedLanguage);
    }
  }

  setLanguage(language: string): void {
    if (this.isValidLanguage(language)) {
      this.currentLanguageSubject.next(language);
      localStorage.setItem('app-language', language);
      document.documentElement.lang = language;
    }
  }

  getCurrentLanguage(): string {
    return this.currentLanguageSubject.value;
  }

  translate(key: string): string {
    const currentLang = this.getCurrentLanguage();
    const translation = this.translations[key];
    
    if (translation && translation[currentLang]) {
      return translation[currentLang];
    }
    
    // Fallback vers le français si la traduction n'existe pas
    if (translation && translation['fr']) {
      return translation['fr'];
    }
    
    // Retourner la clé si aucune traduction n'est trouvée
    return key;
  }

  private isValidLanguage(language: string): boolean {
    return ['fr', 'en', 'es'].includes(language);
  }

  getAvailableLanguages(): { code: string; name: string }[] {
    return [
      { code: 'fr', name: 'Français' },
      { code: 'en', name: 'English' },
      { code: 'es', name: 'Español' }
    ];
  }
}