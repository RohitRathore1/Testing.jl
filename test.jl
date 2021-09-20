function vtk_volume(; kwargs...) 
    return vtk_imagedata(
        kwargs[:state, :image],
        children=[
            vtk_pointdata([
                vtk_dataarray(
                    kwargs[:state, :field],
                )
            ])
        ]
    )
end