import dash_vtk
import numpy as np
import dash
import dash_html_components as html

try:
    # v9 and above
    from vtkmodules.util.numpy_support import vtk_to_numpy
    from vtkmodules.vtkFiltersGeometry import vtkGeometryFilter
except:
    # v8.1.2 and below
    print("Can't import vtkmodules. Falling back to importing vtk.")
    from vtk.util.numpy_support import vtk_to_numpy
    from vtk.vtkFiltersGeometry import vtkGeometryFilter

# Numpy to JS TypedArray
to_js_type = {
    "int8": "Int8Array",
    "uint8": "Uint8Array",
    "int16": "Int16Array",
    "uint16": "Uint16Array",
    "int32": "Int32Array",
    "uint32": "Uint32Array",
    "int64": "Int32Array",
    "uint64": "Uint32Array",
    "float32": "Float32Array",
    "float64": "Float64Array",
}

def to_mesh_state(dataset, field_to_keep=None, point_arrays=None, cell_arrays=None):
    """Expect any dataset and extract its surface into a dash_vtk.Mesh state property"""
    if dataset is None:
        return None

    if point_arrays is None:
        point_arrays = []
    if cell_arrays is None:
        cell_arrays = []

    # Make sure we have a polydata to export
    polydata = None
    if dataset.IsA("vtkPolyData"):
        polydata = dataset
    else:
        extractSkinFilter = vtkGeometryFilter()
        extractSkinFilter.SetInputData(dataset)
        extractSkinFilter.Update()
        polydata = extractSkinFilter.GetOutput()

    if polydata.GetPoints() is None:
        return None

    # Extract mesh
    points = vtk_to_numpy(polydata.GetPoints().GetData())
    verts = (
        vtk_to_numpy(polydata.GetVerts().GetData())
        if polydata.GetVerts()
        else []
    )
    lines = (
        vtk_to_numpy(polydata.GetLines().GetData())
        if polydata.GetLines()
        else []
    )
    polys = (
        vtk_to_numpy(polydata.GetPolys().GetData())
        if polydata.GetPolys()
        else []
    )
    strips = (
        vtk_to_numpy(polydata.GetStrips().GetData())
        if polydata.GetStrips()
        else []
    )

    # Extract field
    values = None
    js_types = "Float32Array"
    nb_comp = 1
    dataRange = [0, 1]
    location = None
    if field_to_keep is not None:
        p_array = polydata.GetPointData().GetArray(field_to_keep)
        c_array = polydata.GetCellData().GetArray(field_to_keep)

        if c_array:
            dataRange = c_array.GetRange(-1)
            nb_comp = c_array.GetNumberOfComponents()
            values = vtk_to_numpy(c_array)
            js_types = to_js_type[str(values.dtype)]
            location = "CellData"

        if p_array:
            dataRange = p_array.GetRange(-1)
            nb_comp = p_array.GetNumberOfComponents()
            values = vtk_to_numpy(p_array)
            js_types = to_js_type[str(values.dtype)]
            location = "PointData"

    # other arrays (points)
    point_data = []
    for name in point_arrays:
        array = polydata.GetPointData().GetArray(name)
        if array:
            dataRange = array.GetRange(-1)
            nb_comp = array.GetNumberOfComponents()
            values = vtk_to_numpy(array)
            js_types = to_js_type[str(values.dtype)]
            point_data.append(
                {
                    "name": name,
                    "values": values,
                    "numberOfComponents": nb_comp,
                    "type": js_types,
                    "location": "PointData",
                    "dataRange": dataRange,
                }
            )

    # other arrays (cells)
    cell_data = []
    for name in point_arrays:
        array = polydata.GetCellData().GetArray(name)
        if array:
            dataRange = array.GetRange(-1)
            nb_comp = array.GetNumberOfComponents()
            values = vtk_to_numpy(array)
            js_types = to_js_type[str(values.dtype)]
            cell_data.append(
                {
                    "name": name,
                    "values": values,
                    "numberOfComponents": nb_comp,
                    "type": js_types,
                    "location": "CellData",
                    "dataRange": dataRange,
                }
            )

    state = {
        "mesh": {"points": points,},
    }
    if len(verts):
        state["mesh"]["verts"] = verts
    if len(lines):
        state["mesh"]["lines"] = lines
    if len(polys):
        state["mesh"]["polys"] = polys
    if len(strips):
        state["mesh"]["strips"] = strips

    if values is not None:
        state.update(
            {
                "field": {
                    "name": field_to_keep,
                    "values": values,
                    "numberOfComponents": nb_comp,
                    "type": js_types,
                    "location": location,
                    "dataRange": dataRange,
                },
            }
        )

    if len(point_data):
        state.update({"pointArrays": point_data})
    if len(cell_data):
        state.update({"cellArrays": cell_data})

    return state

try:
    # VTK 9+
    from vtkmodules.vtkImagingCore import vtkRTAnalyticSource
except:
    # VTK =< 8
    from vtk.vtkImagingCore import vtkRTAnalyticSource

# Use VTK to get some data
data_source = vtkRTAnalyticSource()
data_source.Update()  # <= Execute source to produce an output
dataset = data_source.GetOutput()

# Use helper to get a mesh structure that can be passed as-is to a Mesh
# RTData is the name of the field
mesh_state = to_mesh_state(dataset)

content = dash_vtk.View([
    dash_vtk.GeometryRepresentation([
        dash_vtk.Mesh(state=mesh_state)
    ]),
])

# Dash setup
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(
    style={"width": "100%", "height": "400px"},
    children=[content],
)

if __name__ == "__main__":
    app.run_server(debug=True)