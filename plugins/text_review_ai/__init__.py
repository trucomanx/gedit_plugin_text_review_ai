
from gi.repository import GObject, Gtk, Gedit, PeasGtk, Gio

import os
import json
from . import consulta_di as cdi


CONFIG_BASE_DIR="~/.config/gedit/plugins/text_review_ai"
CONFIG_JSON_FILENAME="text_review_ai.json"

def is_empty_or_whitespace(text):
    # Remove espaços em branco do início e do fim e verifica se a string resultante está vazia
    return not text.strip()

def ler_json_como_dict(filename):
    # Obter o diretório home do usuário
    base_dir = os.path.expanduser(CONFIG_BASE_DIR)
    
    # Construir o caminho completo do arquivo
    caminho_arquivo = os.path.join(base_dir, filename)
    
    # Verificar se o arquivo JSON existe
    if os.path.isfile(caminho_arquivo):
        try:
            # Abrir e carregar o conteúdo do arquivo JSON
            with open(caminho_arquivo, 'r') as json_file:
                data = json.load(json_file)
            return data  # Retornar o conteúdo como dict
        except json.JSONDecodeError:
            print(f"Error decoding file '{caminho_arquivo}'.")
            return None
    else:
        print(f"The file '{caminho_arquivo}' was not found.")
        return None

def escreve_dict_como_json(filename, data):
    # Obter o diretório home do usuário
    base_dir = os.path.expanduser(CONFIG_BASE_DIR)
    
    os.makedirs(base_dir,exist_ok=True);
    
    # Construir o caminho completo do arquivo
    caminho_arquivo = os.path.join(base_dir, filename)
  
    # Criar e salvar o arquivo JSON
    with open(caminho_arquivo, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    
    print(f"The file '{caminho_arquivo}' was created with '{data}'.")
    return True
        
def verifica_ou_cria_json(filename, default_apikey="", default_host="https://api.deepinfra.com/v1/openai", default_model="meta-llama/Meta-Llama-3.1-70B-Instruct"):
    # Obter o diretório base do usuário
    base_dir = os.path.expanduser(CONFIG_BASE_DIR)
    
    os.makedirs(base_dir,exist_ok=True);
    
    # Construir o caminho completo do arquivo
    caminho_arquivo = os.path.join(base_dir, filename)
    
    # Verificar se o arquivo existe
    if os.path.isfile(caminho_arquivo):
        print(f"The file '{caminho_arquivo}' already exists.")
        return True
    else:
        # Se o arquivo não existe, criar um novo arquivo JSON com a chave "language"
        data = {"apikey": default_apikey, "host":default_host, "model":default_model}
        
        # Criar e salvar o arquivo JSON
        with open(caminho_arquivo, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        
        print(f"The file '{caminho_arquivo}' was created with '{data}'.")
        return True


################################################################################
# For our example application, this class is not exactly required.
# But we had to make it because we needed the app menu extension to show the menu.
class TextReviewAIAppActivatable(GObject.Object, Gedit.AppActivatable):
    app = GObject.property(type=Gedit.App)
    __gtype_name__ = "TextReviewAIAppActivatable"

    def __init__(self):
        GObject.Object.__init__(self)
        self.menu_ext = None
        self.menu_item = None
        verifica_ou_cria_json(CONFIG_JSON_FILENAME);

    def do_activate(self):
        self._build_menu()

    def _build_menu(self):
    
        review_shortcut = "<Ctrl><Shift>k"

        # Get the extension from tools menu        
        self.menu_ext = self.extend_menu("tools-section")
        # This is the submenu which is added to a menu item and then inserted in tools menu.        
        sub_menu = Gio.Menu()
        sub_menu_review   = Gio.MenuItem.new("Review the selected text "+review_shortcut, 'win.review_selected_text')
        sub_menu.append_item(sub_menu_review)

        
        self.menu_item = Gio.MenuItem.new_submenu("Text Review AI", sub_menu)
        self.menu_ext.append_menu_item(self.menu_item)
        
        # Setting accelerators, now our action is called when Ctrl+Alt+1 is pressed.
        self.app.set_accels_for_action("win.review_selected_text", (review_shortcut, None))


    def do_deactivate(self):
        self._remove_menu()

    def _remove_menu(self):
        # removing accelerator and destroying menu items
        self.app.set_accels_for_action("win.dictonator_start", ())
        self.menu_ext = None
        self.menu_item = None
        

            


################################################################################
class TextReviewAIWindowActivatable(GObject.Object, Gedit.WindowActivatable, PeasGtk.Configurable):
    window = GObject.property(type=Gedit.Window)
    __gtype_name__ = "TextReviewAIWindowActivatable"

    def __init__(self):
        GObject.Object.__init__(self)
        # This is the attachment we will make to bottom panel.
        self.bottom_bar = Gtk.Box()
        self.info=None;
    
    #this is called every time the gui is updated
    def do_update_state(self):
        # if there is no document in sight, we disable the action, so we don't get NoneException
        if self.window.get_active_view() is not None:
            self.window.lookup_action('review_selected_text').set_enabled(True)

    def do_activate(self):
        # Defining the action which was set earlier in AppActivatable.
        self._connect_menu()
        #self._insert_bottom_panel()

    def _connect_menu(self):
        action_review = Gio.SimpleAction(name='review_selected_text')
        action_review.connect('activate', self.action_cb)
        self.window.add_action(action_review)
    
    
    def text_to_review(self, action):

        view = self.window.get_active_view()
        if not view:
            print("Error: No active view found")
            return

        doc = view.get_buffer()
        start_iter, end_iter = doc.get_selection_bounds()

        if not start_iter or not end_iter:
            print("Error: No selection bounds")
            return

        selected_text = doc.get_text(start_iter, end_iter, False)
        if not selected_text:
            print("Error: No text selected")
            return
        
        self.info=ler_json_como_dict(CONFIG_JSON_FILENAME);

        
        #print(selected_text)
        #print(self.info)
        
        #######################################
        ## TU CODIGO DE COMPARAÇÂO VAI AQUI
        #######################################
        cdi.consulta_deepinfra(self.info["host"],self.info["apikey"],selected_text, self.info["model"])
            
    def action_cb(self, action, data):
        # On action clear the document.
        #doc = self.window.get_active_document()
        #doc.set_text("")
        self.text_to_review(action)


    def _insert_bottom_panel(self):
        # Add elements to panel.
        self.bottom_bar.add(Gtk.Label("Hello There!"))
        # Get bottom bar (A Gtk.Stack) and add our bar.        
        panel = self.window.get_bottom_panel()
        panel.add_titled(self.bottom_bar, 'example', "Example")
        # Make sure everything shows up.
        panel.show()
        self.bottom_bar.show_all()
        panel.set_visible_child(self.bottom_bar)

    def do_deactivate(self):
        self._remove_bottom_panel()

    def _remove_bottom_panel(self):
        panel = self.window.get_bottom_panel()
        panel.remove(self.bottom_bar)

    def do_create_configure_widget(self):
        # 
        self.info=ler_json_como_dict(CONFIG_JSON_FILENAME)
        
        # Criar uma caixa vertical para a interface de configuração
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        # Adicionar uma entrada de texto (Gtk.Label) 
        path = os.path.join(os.path.expanduser(CONFIG_BASE_DIR),CONFIG_JSON_FILENAME);
        label = Gtk.Label()
        label.set_markup("Config file: <a href=\"file://"+path+"\">"+path+"</a>")
        vbox.pack_start(label, False, False, 0)

        # Adicionar uma entrada de texto (Gtk.Label) 
        label = Gtk.Label(label="Enter the the host of AI:")
        vbox.pack_start(label, False, False, 0)

        # Entrada de texto para a configuração do host
        self.entry_host = Gtk.Entry()
        self.entry_host.set_text(self.info['host'].strip())  # Valor padrão
        vbox.pack_start(self.entry_host, False, False, 0)

        # Adicionar uma entrada de texto (Gtk.Label) 
        label = Gtk.Label(label="Enter the the model of AI:")
        vbox.pack_start(label, False, False, 0)

        # Entrada de texto para a configuração do port
        self.entry_model = Gtk.Entry()
        self.entry_model.set_text(self.info['model'].strip())  # Valor padrão
        vbox.pack_start(self.entry_model, False, False, 0)
        
        # Adicionar uma entrada de texto (Gtk.Entry) para o usuário configurar o idioma
        label = Gtk.Label(label="Enter the api key of AI:")
        vbox.pack_start(label, False, False, 0)

        # Entrada de texto para a configuração do idioma
        self.entry_apikey = Gtk.Entry()
        self.entry_apikey.set_text(self.info['apikey'].strip())  # Valor padrão
        vbox.pack_start(self.entry_apikey, False, False, 0)

        # Botão para salvar as configurações
        button = Gtk.Button(label="Save Settings")
        button.connect("clicked", self.on_save_button_clicked)
        vbox.pack_start(button, False, False, 0)

        return vbox
       
    def on_save_button_clicked(self, widget):
        # Quando o botão é clicado, obtemos o texto digitado e salvamos a configuração
        data=dict();
        data['host'] = self.entry_host.get_text().strip()
        data['model'] = self.entry_model.get_text().strip()
        data['apikey'] = self.entry_apikey.get_text().strip()
        escreve_dict_como_json(CONFIG_JSON_FILENAME, data)
        print(f"Plugin set to: {data}")
