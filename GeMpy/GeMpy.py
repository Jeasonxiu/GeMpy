"""
Module with classes and methods to perform implicit regional modelling based on
the potential field method.
Tested on Ubuntu 14

Created on 10/10 /2016

@author: Miguel de la Varga

this is only to test git 3

"""

# import theano
# import theano.tensor as T
import numpy as _np
# import sys, os
# import pandas as pn

from Visualization import PlotData
from DataManagement import DataManagement


def compute_block_model(geo_data, series_number="all",
                        series_distribution=None, order_series=None,
                        extent=None, resolution=None, grid_type="regular_3D",
                        verbose=0, **kwargs):

    if extent or resolution:
        set_grid(geo_data, extent=extent, resolution=resolution, grid_type=grid_type, **kwargs)

    if series_distribution:
        set_data_series(geo_data, series_distribution=series_distribution, order_series=order_series, verbose=0)

    if not getattr(geo_data, 'interpolator', None):
        import warnings

        warnings.warn('Using default interpolation values')
        set_interpolator(geo_data)

    geo_data.interpolator.block.set_value(_np.zeros_like(geo_data.grid.grid[:, 0]))

    geo_data.interpolator.compute_block_model(series_number=series_number, verbose=verbose)

    return geo_data.interpolator.block


def get_grid(geo_data):
    return geo_data.grid.grid


def get_raw_data(geo_data, dtype='all'):
    return geo_data.get_raw_data(dtype=dtype)


def import_data(extent, resolution=[50, 50, 50], **kwargs):
    """
    Method to initialize the class data. Calling this function some of the data has to be provided (TODO give to
    everything a default).

    Args:
        extent (list or array):  [x_min, x_max, y_min, y_max, z_min, z_max]. Extent for the visualization of data
         and default of for the grid class.
        resolution (list or array): [nx, ny, nz]. Resolution for the visualization of data
         and default of for the grid class.
        **kwargs: Arbitrary keyword arguments.

    Keyword Args:
        Resolution ((Optional[list])): [nx, ny, nz]. Defaults to 50
        path_i: Path to the data bases of interfaces. Default os.getcwd(),
        path_f: Path to the data bases of foliations. Default os.getcwd()

    Returns:
        GeMpy.DataManagement: Object that encapsulate all raw data of the project


        dep: self.Plot(GeMpy_core.PlotData): Object to visualize data and results
    """

    return DataManagement(extent, resolution, **kwargs)


def i_set_data(geo_data, dtype="foliations"):

    geo_data.i_set_data(dtype=dtype)


def set_data_series(geo_data, series_distribution=None, order_series=None,
                        update_p_field=True, verbose=0):

    geo_data.set_series(series_distribution=series_distribution, order=order_series)
    try:
        if update_p_field:
            geo_data.interpolator.update_potential_fields()
    except AttributeError:
        pass

    if verbose > 0:
        return get_raw_data(geo_data)


def set_interfaces(geo_data, interf_Dataframe, append=False, update_p_field = True):
    geo_data.set_interfaces(interf_Dataframe, append=append)
    # To update the interpolator parameters without calling a new object
    try:
        geo_data.interpolator._data = geo_data
        geo_data.interpolator._grid = geo_data.grid
       # geo_data.interpolator._set_constant_parameteres(geo_data, geo_data.interpolator._grid)
        if update_p_field:
            geo_data.interpolator.update_potential_fields()
    except AttributeError:
        pass


def set_foliations(geo_data, foliat_Dataframe, append=False, update_p_field=True):
    geo_data.set_foliations(foliat_Dataframe, append=append)
    # To update the interpolator parameters without calling a new object
    try:
        geo_data.interpolator._data = geo_data
        geo_data.interpolator._grid = geo_data.grid
      #  geo_data.interpolator._set_constant_parameteres(geo_data, geo_data.interpolator._grid)
        if update_p_field:
            geo_data.interpolator.update_potential_fields()
    except AttributeError:
        pass


def set_grid(geo_data, extent=None, resolution=None, grid_type="regular_3D", **kwargs):
    """
    Method to initialize the class grid. So far is really simple and only has the regular grid type

    Args:
        grid_type (str): regular_3D or regular_2D (I am not even sure if regular 2D still working)
        **kwargs: Arbitrary keyword arguments.

    Returns:
        self.grid(GeMpy_core.grid): Object that contain different grids
    """
    if not extent:
        extent = geo_data.extent
    if not resolution:
        resolution = geo_data.resolution

    geo_data.grid = geo_data.GridClass(extent, resolution, grid_type=grid_type, **kwargs)


def set_interpolator(geo_data, compile_theano=False, *args, **kwargs):
    """
    Method to initialize the class interpolator. All the constant parameters for the interpolation can be passed
    as args, otherwise they will take the default value (TODO: documentation of the dafault values)

    Args:
        *args: Variable length argument list
        **kwargs: Arbitrary keyword arguments.

    Keyword Args:
        range_var: Range of the variogram. Default None
        c_o: Covariance at 0. Default None
        nugget_effect: Nugget effect of the gradients. Default 0.01
        u_grade: Grade of the polynomial used in the universal part of the Kriging. Default 2
        rescaling_factor: Magic factor that multiplies the covariances). Default 2

    Returns:
        self.Interpolator (GeMpy_core.Interpolator): Object to perform the potential field method
        self.Plot(GeMpy_core.PlotData): Object to visualize data and results. It gets updated.
    """

    if not getattr(geo_data, 'grid', None):
        set_grid(geo_data)

    if not getattr(geo_data, 'interpolator', None) or compile_theano:
        geo_data.interpolator = geo_data.InterpolatorClass(geo_data, geo_data.grid, compile_theano=True,
                                                           *args, **kwargs)
    else:
        geo_data.interpolator._data = geo_data
        geo_data.interpolator._grid = geo_data.grid
        geo_data.interpolator._set_constant_parameteres(geo_data, geo_data.interpolator._grid, **kwargs)


def plot_data(geo_data, direction="y", series="all", **kwargs):
    plot = PlotData(geo_data)
    plot.plot_data(direction=direction, series=series, **kwargs)
    # TODO saving options
    return plot


def plot_section(geo_data, cell_number, block=None, direction="y", **kwargs):
    plot = PlotData(geo_data)
    plot.plot_block_section(cell_number, block=block, direction=direction, **kwargs)
    # TODO saving options
    return plot


def plot_potential_field(geo_data, cell_number, potential_field=None, n_pf=0,
                         direction="y", plot_data=True, series="all", *args, **kwargs):

    plot = PlotData(geo_data)
    plot.plot_potential_field(cell_number, potential_field=potential_field, n_pf=n_pf,
                              direction=direction,  plot_data=plot_data, series=series,
                              *args, **kwargs)


def update_potential_fields(geo_data, verbose=0):
    geo_data.interpolator.update_potential_fields(verbose=verbose)