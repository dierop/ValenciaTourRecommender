def asignar_grupos(usuario):
    """
    Asigna todos los grupos posibles a un usuario basado en su ocupación, edad y número de hijos.
    Devuelve una lista con los nombres de los grupos a los que pertenece.
    """
    grupos = []

    if (usuario['id_occupation'] == 1 and
        usuario['children'] == 0 and
        usuario['young_children_age'] == 0):
        grupos.append('fuerzas armadas sin hijos')

    if (usuario['sex'] == 'M' and
        usuario['age'] < 30 and
        usuario['children'] == 0):
        grupos.append('hombre joven sin hijos')

    if (usuario['sex'] == 'F' and
        usuario['age'] < 30 and
        usuario['children'] == 0):
        grupos.append('mujeres jovenes sin hijos')

    if (usuario['children'] == 1 and
        ((0 < usuario['young_children_age'] < 5) or
         (usuario['young_children_age'] == 0 and usuario['older_children_age'] < 5))):
        grupos.append('con hijos pequenos')

    if (usuario['children'] == 1 and
        30 < usuario['age'] < 55):
        grupos.append('media edad con hijos')

    if ((usuario['id_occupation'] == 11 or usuario['age'] >= 60) and
        (usuario['young_children_age'] > 25 or usuario['children'] == 0)):
        grupos.append('personas con tiempo libre')

    if (usuario['id_occupation'] in [3, 4] and
        usuario['children'] > 0):
        grupos.append('tecnicos profesionales con hijos')

    if (usuario['id_occupation'] in [3, 4] and
        usuario['children'] == 0):
        grupos.append('tecnicos_profesionales sin hijos')

    if (30 <= usuario['age'] <= 40 and
        usuario['children'] == 0):
        grupos.append('entre treinta y cuarenta sin hijos')

    if not grupos:
        grupos.append('sin_grupo')

    return grupos
