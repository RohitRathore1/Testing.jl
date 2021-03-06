using DashVtk
using DashBase
using PyCall

vtk = pyimport("vtkmodules.vtkFiltersGeometry")

to_js_type = Dict(
    "Int16" => "Int16Array",
    "Int32" => "Int32Array",
    "Int64" => "Int64Array",
    "Float32" => "Float32Array",
    "Float64" => "Float64Array"
)

function to_mesh_state(dataset, point_arrays=nothing, cell_arrays=nothing) 
    """
    Expect any dataset and extract its surface into a 
    """
    if dataset == nothing
        return nothing
    end
    if point_arrays == nothing
        point_arrays = []
    end
    if cell_arrays == nothing
        cell_arrays = []
    end

    #Make sure we have a polydata to export
    #polydata = nothing
    #if DashBase.get_type(dataset) == "vtk_polydata"
    #    polydata = dataset

    #else
     #   extractSkinFilter = vtk.vtkGeometryFilter()
      #  extractSkinFilter.SetInputData(dataset)
      #  extractSkinFilter.Update()
      #  polydata = extractSkinFilter.GetOutput()
   # end

   polydata  = dataset

    if polydata.points[] == nothing
        return nothing
    end

    # Extract mesh 
    points = polydata.points().data()
    verts = Dict(
        polydata.points().data()
        if polydata.verts()
        else []
        end
    )
    lines = Dict(
        polydata.lines().data()
        if polydata.lines()
        else []
        end
    )
    polys = Dict(
        polydata.polys().data()
        if polydata.polys()
        else []
        end
    )
    strips = Dict(
        polydata.strips().data()
        if polydata.strips()
        else []
        end
    )

    # Extract field
    values = nothing
    js_types = "Float32Array"
    nb_comp = 1
    dataRange = [0, 1]
    location = nothing
    if field_to_keep != nothing
        p_array = polydata.PointData().Array(field_to_keep)
        c_array = polydata.CellData().Array(field_to_keep)

        if c_array:
            dataRange = c_array.Range(-1)
            nb_comp = c_array.NumberOfComponents()
            values = c_array
            js_types = to_js_type[str(values.dtype)]
            location = "PointData"
    end
    return state
    
end

dataset =  vtk_polydata(
    points = [
       0, 0, 0,
       1, 0, 0,
       0, 1, 0,
       1, 1, 0,
    ],
    lines = [3, 1, 3, 2],
    polys = [3, 0, 1, 2],
    children = [
           vtk_pointdata([
               vtk_dataarray(
                  #registration='setScalars', # To activate field
                  name="onPoints",
                  values = [0, 0.33, 0.66, 1],

               )
           ]),
           vtk_celldata([
               vtk_dataarray(
                   # registration='setScalars', # To activate field
                   name="onCells",
                   values=[0, 1],
               )
           ])
        ],
      )

mesh_state = to_mesh_state(dataset)