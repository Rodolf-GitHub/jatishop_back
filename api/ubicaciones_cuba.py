PROVINCIAS_MUNICIPIOS = {
    'Pinar del Río': [
        'Consolación del Sur', 'Guane', 'La Palma', 'Los Palacios', 'Mantua',
        'Minas de Matahambre', 'Pinar del Río', 'San Juan y Martínez', 
        'San Luis', 'Sandino', 'Viñales'
    ],
    'Artemisa': [
        'Alquízar', 'Artemisa', 'Bauta', 'Caimito', 'Guanajay', 'Güira de Melena',
        'Mariel', 'San Antonio de los Baños', 'Bahía Honda', 'San Cristóbal', 'Candelaria'
    ],
    'La Habana': [
        'Playa', 'Plaza de la Revolución', 'Centro Habana', 'La Habana Vieja',
        'Regla', 'La Habana del Este', 'Guanabacoa', 'San Miguel del Padrón',
        'Diez de Octubre', 'Cerro', 'Marianao', 'La Lisa', 'Boyeros',
        'Arroyo Naranjo', 'Cotorro'
    ],
    'Mayabeque': [
        'Bejucal', 'San José de las Lajas', 'Jaruco', 'Santa Cruz del Norte',
        'Madruga', 'Nueva Paz', 'San Nicolás', 'Güines', 'Melena del Sur',
        'Batabanó', 'Quivicán'
    ],
    'Matanzas': [
        'Calimete', 'Cárdenas', 'Ciénaga de Zapata', 'Colón', 'Jagüey Grande',
        'Jovellanos', 'Limonar', 'Los Arabos', 'Martí', 'Matanzas', 'Pedro Betancourt',
        'Perico', 'Unión de Reyes'
    ],
    'Cienfuegos': [
        'Abreus', 'Aguada de Pasajeros', 'Cienfuegos', 'Cruces', 'Cumanayagua',
        'Palmira', 'Rodas', 'Santa Isabel de las Lajas'
    ],
    'Villa Clara': [
        'Caibarién', 'Camajuaní', 'Cifuentes', 'Corralillo', 'Encrucijada',
        'Manicaragua', 'Placetas', 'Quemado de Güines', 'Ranchuelo',
        'Remedios', 'Sagua la Grande', 'Santa Clara', 'Santo Domingo'
    ],
    'Sancti Spíritus': [
        'Cabaiguán', 'Fomento', 'Jatibonico', 'La Sierpe', 'Sancti Spíritus',
        'Taguasco', 'Trinidad', 'Yaguajay'
    ],
    'Ciego de Ávila': [
        'Ciro Redondo', 'Baraguá', 'Bolivia', 'Chambas', 'Ciego de Ávila',
        'Florencia', 'Majagua', 'Morón', 'Primero de Enero', 'Venezuela'
    ],
    'Camagüey': [
        'Camagüey', 'Carlos Manuel de Céspedes', 'Esmeralda', 'Florida',
        'Guáimaro', 'Jimaguayú', 'Minas', 'Najasa', 'Nuevitas', 'Santa Cruz del Sur',
        'Sibanicú', 'Sierra de Cubitas', 'Vertientes'
    ],
    'Las Tunas': [
        'Amancio', 'Colombia', 'Jesús Menéndez', 'Jobabo', 'Las Tunas',
        'Majibacoa', 'Manatí', 'Puerto Padre'
    ],
    'Holguín': [
        'Antilla', 'Báguanos', 'Banes', 'Cacocum', 'Calixto García',
        'Cueto', 'Frank País', 'Gibara', 'Holguín', 'Mayarí',
        'Moa', 'Rafael Freyre', 'Sagua de Tánamo', 'Urbano Noris'
    ],
    'Granma': [
        'Bartolomé Masó', 'Bayamo', 'Buey Arriba', 'Campechuela', 'Cauto Cristo',
        'Guisa', 'Jiguaní', 'Manzanillo', 'Media Luna', 'Niquero',
        'Pilón', 'Río Cauto', 'Yara'
    ],
    'Santiago de Cuba': [
        'Contramaestre', 'Guamá', 'Julio Antonio Mella', 'Palma Soriano',
        'San Luis', 'Santiago de Cuba', 'Segundo Frente', 'Songo-La Maya',
        'Tercer Frente'
    ],
    'Guantánamo': [
        'Baracoa', 'Caimanera', 'El Salvador', 'Guantánamo', 'Imías',
        'Maisí', 'Manuel Tames', 'Niceto Pérez', 'San Antonio del Sur',
        'Yateras'
    ],
    'Isla de la Juventud': [
        'Nueva Gerona'
    ]
}

# Lista simple de provincias
PROVINCIAS = list(PROVINCIAS_MUNICIPIOS.keys())

# Función helper para obtener municipios de una provincia
def get_municipios(provincia):
    return PROVINCIAS_MUNICIPIOS.get(provincia, []) 