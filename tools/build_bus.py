"""Generate an original, editable articulated test bus. Run with Blender -b -t 2 -P.
Dimensions are design assumptions, not measurements of a commercial vehicle.
Coordinates below use Godot conventions (X right, Y up, forward -Z), in metres.
"""
from pathlib import Path
import bpy
import math
ROOT = Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0

def mat(name, rgb, metal=0, rough=.5, alpha=1):
    m=bpy.data.materials.new(name); m.diffuse_color=(*rgb,alpha); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*rgb,alpha)
    p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    p.inputs['Alpha'].default_value=alpha
    if alpha<1: m.surface_render_method='DITHERED'
    return m
red=mat('Pintura roja',(.52,.012,.018),.2,.3)
dark=mat('Marcos y goma',(.018,.023,.029),0,.7)
glass=mat('Vidrio azulado',(.12,.22,.26),.15,.19,.48)
metal=mat('Aluminio',(.4,.45,.48),.7,.3)
yellow=mat('Franja amarilla',(.98,.58,.045),.1,.4)
inside=mat('Interior gris',(.22,.25,.26),0,.8)
seat=mat('Asientos',(.13,.22,.28),0,.75)
light=mat('Luz blanca',(.95,.93,.8),.1,.22)
tail=mat('Luz posterior',(.7,.02,.008),.1,.2)

def empty(name,parent=None):
    o=bpy.data.objects.new(name,None); scene.collection.objects.link(o);o.parent=parent;return o

def pos(p):return (p[0],-p[2],p[1])

def box(name,p,size,material,parent,bevel=.015):
    bpy.ops.mesh.primitive_cube_add(size=1,location=pos(p))
    o=bpy.context.object;o.name=name;o.dimensions=(size[0],size[2],size[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(material)
    if bevel:
        mod=o.modifiers.new('Bordes suavizados','BEVEL');mod.width=bevel;mod.segments=2
        bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
        mod=o.modifiers.new('Normales','WEIGHTED_NORMAL');bpy.ops.object.modifier_apply(modifier=mod.name)
    o.parent=parent;return o

def cylinder(name,p,radius,depth,material,parent,axis='X'):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=radius,depth=depth,location=pos(p))
    o=bpy.context.object;o.name=name
    if axis=='X':o.rotation_euler[1]=math.pi/2
    o.data.materials.append(material);o.parent=parent
    bevel=o.modifiers.new('Borde','BEVEL');bevel.width=.025;bevel.segments=2
    bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=bevel.name)
    return o
root=empty('BusPrototype')
front=empty('Front',root);rear=empty('Rear',root)
# Rear authored at its hinge origin; preview .blend places it 2.7 m behind Front.
for body,start,end,doors,axles in [(front,-7.4,2.2,[-4.6,-.9],[-5.8,0]),(rear,.5,7.9,[2,5.9],[5.4])]:
    length=end-start;mid=(start+end)/2
    box('Suelo',(0,1.04,mid),(2.45,.18,length-.12),inside,body)
    box('Techo',(0,3.12,mid),(2.53,.18,length-.15),red,body,.06)
    box('Equipo_techo',(0,3.23,mid+.6),(1.8,.15,min(3,length-1)),inside,body,.08)
    for side in [-1,1]:
        openings=doors if side==-1 else []
        edges=[start]+[v for z in openings for v in (z-.68,z+.68)]+[end]
        spans=[(edges[i],edges[i+1]) for i in range(0,len(edges)-1,2)]
        for a,b in spans:
            box('Panel',(side*1.225,1.4,(a+b)/2),(.1,.8,b-a),red,body,.025)
            box('Franja',(side*1.281,1.72,(a+b)/2),(.016,.15,b-a),yellow,body,.003)
            box('Ventana',(side*1.232,2.4,(a+b)/2),(.035,1.06,max(.03,b-a-.08)),glass,body,.02)
        # Window mullions, avoiding openings.
        for j in range(math.ceil(length/1.5)+1):
            z=min(end-.04,start+.04+j*1.5)
            if any(abs(z-d)<.72 for d in openings):continue
            box('Pilar',(side*1.25,2.43,z),(.06,1.3,.07),dark,body,.009)
        box('Marco_superior',(side*1.255,2.99,mid),(.06,.09,length),dark,body)
        for d in openings:
            for sign in [-1,1]:
                z=d+sign*.32
                leaf=empty('Door_%s_%s_%s'%(body.name,d,'minus' if sign<0 else 'plus'),body)
                leaf.location=pos((0,0,z))
                box('Hoja_puerta',(-1.251,1.58,0),(.075,1.08,.61),red,leaf)
                box('Vidrio_puerta',(-1.259,2.46,0),(.055,.68,.53),glass,leaf)
                for edge in [-.305,.305]:box('Marco_puerta',(-1.29,1.97,edge),(.04,1.85,.035),dark,leaf)
            for edge in [-.71,.71]:box('Jamba',(-1.26,1.99,d+edge),(.09,2,.06),dark,body)
    # Tires remain separate for wheel rotation; steer pivots rotate around Y in Godot.
    for axle in axles:
        for side in [-1,1]:
            pivot=empty('SteerWheel' if body==front and axle==-5.8 else 'Wheel',body)
            pivot.location=pos((side*1.13,.52,axle))
            cylinder('Neumatico',(0,0,0),.51,.27,dark,pivot)
            cylinder('Llanta',(side*.145,0,0),.29,.02,metal,pivot)
            cylinder('Centro',(side*.16,0,0),.115,.06,inside,pivot)
    for z in [start+1.0+i*1.05 for i in range(int(length-1))]:
        if body==front and z<-5.5: continue
        for side in [-1,1]:
            if side==-1 and any(abs(z-d)<.8 for d in doors):continue
            box('Asiento',(side*.86,1.49,z),(.5,.13,.45),seat,body,.05)
            box('Respaldo',(side*.86,1.85,z+.2),(.5,.65,.09),seat,body,.045)
    box('Pasamanos_superior',(0,2.87,mid),(.035,.035,length-.6),yellow,body)
# Open windscreen above the dashboard gives a usable interior camera view.
box('Morro',(0,1.43,-7.32),(2.49,.82,.16),red,front,.06)
box('Parabrisas',(0,2.37,-7.31),(2.38,1.12,.025),glass,front,.04)
box('Marco_frontal',(0,2.99,-7.31),(2.45,.13,.06),dark,front)
box('Parachoques',(0,.81,-7.37),(2.4,.21,.14),dark,front,.035)
box('Letrero_frontal',(0,2.87,-7.34),(1.62,.21,.06),dark,front)
for side in [-1,1]:
    box('Faro',(side*.92,1.37,-7.42),(.33,.17,.025),light,front)
    box('Pilar_frontal',(side*1.23,2.36,-7.31),(.07,1.2,.08),dark,front)
    box('Retrovisor',(side*1.43,2.62,-6.93),(.16,.36,.15),dark,front,.04)
box('Panel_trasero',(0,2.02,7.82),(2.46,2.08,.15),red,rear,.04)
box('Ventana_trasera',(0,2.48,7.91),(2.02,.76,.03),glass,rear)
box('Parachoques_trasero',(0,.82,7.85),(2.4,.23,.13),dark,rear)
for side in [-1,1]:box('Piloto_trasero',(side*1.05,1.45,7.93),(.18,.35,.025),tail,rear)
box('Tablero',(-.52,1.81,-6.82),(1.32,.28,.52),inside,front,.08)
box('Instrumentos',(-.6,1.98,-6.89),(.64,.04,.24),dark,front)
box('Asiento_conductor',(-.68,1.57,-5.97),(.56,.18,.58),seat,front,.05)
box('Respaldo_conductor',(-.68,1.99,-5.67),(.56,.74,.13),seat,front,.05)
bpy.ops.mesh.primitive_torus_add(major_radius=.215,minor_radius=.023,major_segments=32,minor_segments=8,location=pos((-.64,2.05,-6.49)))
o=bpy.context.object;o.name='Volante';o.data.materials.append(dark);o.parent=front
box('Columna_volante',(-.64,1.89,-6.49),(.07,.3,.07),inside,front)
# GLB contains independent bodies at the origin; the engine positions the rear at the hinge.
for obj in bpy.context.selected_objects:obj.select_set(False)
for obj in bpy.data.objects:obj.select_set(True)
bpy.context.view_layer.objects.active=front
bpy.ops.export_scene.gltf(filepath=str(ROOT/'game/assets/vehicles/articulado_prototipo.glb'),export_format='GLB',use_selection=True,export_yup=True)
rear.location=pos((0,0,2.7))
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'assets/source/articulado_prototipo.blend'))
print('BUS_MODEL_READY',len(bpy.data.objects),'objects')
