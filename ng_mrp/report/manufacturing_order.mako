## -*- coding: utf-8 -*-
<html>
<head>
    <style type="text/css">
        ${css}

.list_main_table {
    border:thin solid #E3E4EA;
    text-align:center;
    border-collapse: collapse;
}
table.list_main_table {
    margin-top: 20px;
}
.list_main_headers {
    padding: 0;
}
.list_main_headers th {
    border: thin solid #000000;
    padding-right:3px;
    padding-left:3px;
    background-color: #EEEEEE;
    text-align:center;
    font-size:12;
    font-weight:bold;
}
.list_main_table td {
    padding-right:3px;
    padding-left:3px;
    padding-top:3px;
    padding-bottom:3px;
}
.list_main_lines,
.list_main_footers {
    padding: 0;
}
.list_main_footers {
    padding-top: 15px;
}
.list_main_lines td,
.list_main_footers td,
.list_main_footers th {
    border-style: none;
    text-align:left;
    font-size:12;
    padding:0;
}
.list_main_footers th {
    text-align:right;
}

td .total_empty_cell {
    width: 77%;
}
td .total_sum_cell {
    width: 13%;
}

.nobreak {
    page-break-inside: avoid;
}
caption.formatted_note {
    text-align:left;
    border-right:thin solid #EEEEEE;
    border-left:thin solid #EEEEEE;
    border-top:thin solid #EEEEEE;
    padding-left:10px;
    font-size:11;
    caption-side: bottom;
}
caption.formatted_note p {
    margin: 0;
}

.main_col1 {
    width: 40%;
}
td.main_col1 {
    text-align:left;
}
.main_col2,
.main_col3,
.main_col4,
.main_col6 {
    width: 10%;
}
.main_col5 {
    width: 7%;
}
td.main_col5 {
    text-align: center;
    font-style:italic;
    font-size: 10;
}
.main_col7 {
    width: 13%;
}

.list_bank_table {
    text-align:center;
    border-collapse: collapse;
    page-break-inside: avoid;
    display:table;
}

.act_as_row {
   display:table-row;
}
.list_bank_table .act_as_thead {
    background-color: #EEEEEE;
    text-align:left;
    font-size:12;
    font-weight:bold;
    padding-right:3px;
    padding-left:3px;
    white-space:nowrap;
    background-clip:border-box;
    display:table-cell;
}
.list_bank_table .act_as_cell {
    text-align:left;
    font-size:12;
    padding-right:3px;
    padding-left:3px;
    padding-top:3px;
    padding-bottom:3px;
    white-space:nowrap;
    display:table-cell;
}


.list_tax_table {
}
.list_tax_table td {
    text-align:left;
    font-size:12;
}
.list_tax_table th {
}
.list_tax_table thead {
    display:table-header-group;
}


.list_total_table {
    border:thin solid #E3E4EA;
    text-align:center;
    border-collapse: collapse;
}
.list_total_table td {
    border-top : thin solid #EEEEEE;
    text-align:left;
    font-size:12;
    padding-right:3px;
    padding-left:3px;
    padding-top:3px;
    padding-bottom:3px;
}
.list_total_table th {
    background-color: #EEEEEE;
    border: thin solid #000000;
    text-align:center;
    font-size:12;
    font-weight:bold;
    padding-right:3px
    padding-left:3px
}
.list_total_table thead {
    display:table-header-group;
}

.right_table {
    right: 4cm;
    width:"100%";
}

.std_text {
    font-size:12;
}

th.date {
    width: 90px;
}

td.amount, th.amount {
    text-align: right;
    white-space: nowrap;
}

td.date {
    white-space: nowrap;
    width: 90px;
}

td.vat {
    white-space: nowrap;
}
.address .recipient {
    font-size: 12px;
    margin-left: 350px;
    margin-right: 120px;
    float: right;
}


/* reference: http://stackoverflow.com/questions/10040842/add-border-bottom-to-table-row-tr */
tr.border_bottom_head td {
  border-bottom:2pt solid black;
}
tr.border_bottom_row td { 
  border-bottom:1pt solid #B6B6B4; 
  
}
/* Uncomment this if you want the tables to have joined lines
 * 
 table{ 
    border-collapse: collapse; 
} 
*/


table.withboarder, table.withboarder tr td{
    border: 1px solid #B6B6B4;
    border-collapse: collapse; 
}


    </style>
</head>
<body> 
	<% manufacturing_orders = get_manufacturing_order() %>	
	<table style="text-align:left;" width="100%" >
		<tr  style="text-align: center"  ><td><h1>Product Produced Report</h1></td></tr>
		<tr><td><h3>Product Information</h3></td></tr>
		<tr>
			<td valign="top" >
				<table width="100%" class="withboarder"  >					
					<tr><td><b>Product Produced:</b></td><td>${manufacturing_orders.product_id.name or ''} </td></tr>
					<tr><td><b>Product Qty:</b></td><td>${formatLang(manufacturing_orders.product_qty) or ''} </td></tr>
					<tr><td><b>Scheduled Date:</b></td><td>${manufacturing_orders.date_planned or ''} </td></tr>
					<tr><td><b>Bill of Material:</b></td><td>${manufacturing_orders.bom_id.name or ''} </td></tr>
					<tr><td><b>Production Location:</b></td><td>${manufacturing_orders.routing_id.name or ''} </td></tr>
					<tr><td><b>Production Officer:</b></td><td>${manufacturing_orders.user_id.name or ''} </td></tr>
			   </table>				
			</td>	
		</tr>
		<tr><td><h3>Cost Information</h3></td></tr>
		<tr>
			<td valign="top" >
				<table width="100%" class="withboarder"    >					
					<tr><td><b>Total Workcenter Cost:</b></td><td>${formatLang(manufacturing_orders.total_cost_wc) or ''} </td></tr>
					<tr><td><b>Total Raw Material Cost:</b></td><td>${formatLang(manufacturing_orders.raw_cost) or ''} </td></tr>
					<tr><td><b>Total Production Cost:</b></td><td>${formatLang(manufacturing_orders.total_cost) or ''} </td></tr>
					<tr><td><b>Cost per Unit :</b></td><td>${formatLang(manufacturing_orders.total_cost_unit) or ''} </td></tr>	
				</table>				
			</td>						
		</tr>
	</table>
	
</body>
</html>