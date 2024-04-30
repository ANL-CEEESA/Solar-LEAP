# Solar-LEAP

**Solar-LEAP** is an open-source decision support tool to implement prognostics-based maintennce in real-world solar inverter O&M schedules.

![image](https://github.com/ANL-CEEESA/Solar-LEAP/assets/62155196/065717b3-8d44-4890-a54e-82170758b323)
![image](https://github.com/ANL-CEEESA/Solar-LEAP/assets/62155196/34ff0a69-d196-4b92-b2c6-9252a9b32232)
![image](https://github.com/ANL-CEEESA/Solar-LEAP/assets/62155196/7127a4d5-18f7-41bd-a6ef-d266bfcceff9)
![image](https://github.com/ANL-CEEESA/Solar-LEAP/assets/62155196/4398a62c-83ee-4182-8d0d-cbcc87f502c8)
## Sample Usage

```python
from inv_simulation import inv_simulation, dist_prep, dmc_prep
from draw_plot import draw_plot_f1, draw_plot_f2, draw_plot_f3

# simulation of inverter operation
plot_data [f'i{inv_num}'], [maint_day, maint_type, maint_na_days, maint_cost, ft_sample, day_it] = inv_simulation (inv_num, input_scale_dict, input_c_p, input_c_f, na_days_pm, na_days_cm, simulation_end_days, simulation_step_days, day, day_it, maint_day, maint_type, maint_na_days, maint_cost, ft_sample)
# through (1) failure time prediction; (2) dynamic maintennace cost and (3) maintenance metric summary
draw_plot_f1(inv_num, canvas_fig_ax_dict, day, day_it, plot_data)
draw_plot_f2(inv_num, canvas_fig_ax_dict, day, day_it, plot_data)
draw_plot_f3(inv_num, canvas_fig_ax_dict, day, day_it, plot_data, maint_na_days, maint_cost, eur_proposed)

# GUI developed using PysimpleGUI package.
layout1 = ['input module']
layout2 = ['output module - visulization' ]
layout3 = ['output module - quick results skipping visualization' ]


```


## Authors
* **Shijia Zhao** (Argonne National Laboratory)
* **Liming Liu** (Iowa State University)
* **Murat Yildirim** (Wayne State University)


## Acknowledgments

* This tool is based upon work supported by the U.S. Department of Energy Office of Energy Efficiency and Renewable Energy (EERE) under the Solar Energy Technologies Office Award Number 39640.. 

## Citing

If you use Solar-LEAP in your research (instances, models or algorithms), we kindly request that you cite the package as follows:

* Yi Luo, Liming Liu, Yuxuan Yuan, Zhaoyu Wang, Murat Yildirim, Feng Qiu, Shijia Zhao. **“Data-Driven Assessment of Operational and Harsh Environmental Stress Factors for Solar Inverters using Field Measurements”**, PES-General Meeting, 2024


## License

```text
Solar-LEAP: A Python optimization package for the inspection and maintenance scheduling of marine energy systems.
Copyright © 2022-2024, UChicago Argonne, LLC. All Rights Reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted
provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of
   conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of
   conditions and the following disclaimer in the documentation and/or other materials provided
   with the distribution.
3. Neither the name of the copyright holder nor the names of its contributors may be used to
   endorse or promote products derived from this software without specific prior written
   permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
```
# Solar-LEAP
