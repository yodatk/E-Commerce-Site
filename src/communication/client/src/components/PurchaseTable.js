import React, {Component} from "react";
import {MDBBtn, MDBContainer, MDBLink, MDBRow, MDBTable, MDBTableBody, MDBTableHead} from "mdbreact";
import axios from "axios";
import PropTypes from "prop-types";
import SearchStoresPage from "./Pages/SearchStoresPage";
import OnlyHeaderComponent from "./OnlyHeaderComponent";

export class PurchaseTable extends Component {

    render() {
        if (!(this.props.purchases.length > 0)) {
            return <OnlyHeaderComponent header={"No Purchases Found"}/>
        }
        return (

            <MDBContainer>
                <OnlyHeaderComponent header={"Purchases Found:"}/>

                <MDBTable>
                    <MDBTableHead color="primary-color" textWhite>
                        <tr>
                            <th>#</th>
                            <th>Purchase ID</th>
                            <th>User</th>
                            <th>Store Name</th>
                            <th>Purchase Type</th>
                            <th>Purchase time</th>
                            <th>Total</th>
                        </tr>
                    </MDBTableHead>
                    <MDBTableBody>
                        {this.props.purchases.map((purchase, i) => (
                            <React.Fragment>
                                <tr key={i} className="orange text-white">
                                    <td>{i + 1}</td>
                                    <td>{purchase.purchase_id}</td>
                                    <td>{purchase.user_name}</td>
                                    <td>{purchase.basket.store}</td>
                                    <td>{purchase.purchase_type}</td>
                                    <td>{purchase.time_of_purchase}</td>
                                    <td>{`${purchase.basket.total_price}$`}</td>
                                </tr>
                                <MDBTableHead color="warning-color" textWhite>
                                    <tr>
                                        <th>#</th>
                                        <th>Product Name</th>
                                        <th>quantity</th>
                                        <th>Total Price</th>
                                    </tr>
                                </MDBTableHead>
                                <MDBTableBody>
                                    {
                                        purchase.basket.basket.map((product, j) => {
                                            let total_price = product["total_price"]
                                            let product_name = product["product"]["name"]
                                            let quantity = product["quantity"]
                                            return <tr>
                                                <td>{j + 1}</td>
                                                <td>{product_name}</td>
                                                <td>{quantity}</td>
                                                <td>{`${total_price}$`}</td>
                                            </tr>
                                        })
                                    }
                                </MDBTableBody>
                            </React.Fragment>


                        ))}

                    </MDBTableBody>
                </MDBTable>


            </MDBContainer>
        );
    }
}

// PropTypes
PurchaseTable.propTypes = {
    purchases: PropTypes.array.isRequired,
};

export default PurchaseTable;