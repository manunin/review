import PrimeVue from 'primevue/config'
import 'primevue/resources/themes/aura-light-green/theme.css'
import 'primevue/resources/primevue.min.css'
import 'primeicons/primeicons.css'
import 'primeflex/primeflex.css'

// Import PrimeVue components
import Button from 'primevue/button'
import Card from 'primevue/card'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Dropdown from 'primevue/dropdown'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dialog from 'primevue/dialog'
import ProgressSpinner from 'primevue/progressspinner'
import FileUpload from 'primevue/fileupload'
import DataView from 'primevue/dataview'
import Paginator from 'primevue/paginator'
import Menubar from 'primevue/menubar'
import Panel from 'primevue/panel'
import Menu from 'primevue/menu'
import Avatar from 'primevue/avatar'
import Chip from 'primevue/chip'
import Message from 'primevue/message'

export default function (app) {
  app.use(PrimeVue)
  
  // Register components
  app.component('Button', Button)
  app.component('Card', Card)
  app.component('InputText', InputText)
  app.component('Textarea', Textarea)
  app.component('Dropdown', Dropdown)
  app.component('DataTable', DataTable)
  app.component('Column', Column)
  app.component('Dialog', Dialog)
  app.component('ProgressSpinner', ProgressSpinner)
  app.component('FileUpload', FileUpload)
  app.component('DataView', DataView)
  app.component('Paginator', Paginator)
  app.component('Menubar', Menubar)
  app.component('Panel', Panel)
  app.component('Menu', Menu)
  app.component('Avatar', Avatar)
  app.component('Chip', Chip)
  app.component('Message', Message)
}
