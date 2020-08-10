import React, {Component} from "react";
import {MDBAlert, MDBBtn, MDBCol, MDBContainer, MDBIcon, MDBJumbotron, MDBNavLink, MDBRow} from "mdbreact";
import PropTypes from "prop-types";
import axios from "axios";
import {CONFLICT, OK} from "http-status-codes";
import {Redirect, withRouter} from "react-router-dom";

export class ViewProductPage extends Component {

    state = {
        productName: "",
        productBrand: "",
        productCategories: "",
        description: "",
        quantity: -1,
        discounts: null,
        policies: "",
        storeName: "",
        price: "",
        after_discount: "",
        msg: "",
        redirectAddress: null,

        value_to_cart: 1,

        after_adding_msg: "",
        after_adding_msg_color: "primary"

    }

    addToShoppingCart = (e) => {
        e.preventDefault();
        let user_id = this.props.getUserId()
        let product_name = this.props.match.params.product_name
        let store_name = this.props.match.params.store_name
        let quantity = this.state.value_to_cart

        axios.post(`/add_item_to_shopping_cart`, {
            'product_name': product_name,
            'store_name': store_name,
            'quantity': quantity
        }).then((res) => {
            console.log(res)
            this.dealWithAddProductResult(res)
        }).catch(error => {
            console.log(error)
            this.dealWithAddProductResult(error.response);
        });
    }

    dealWithAddProductResult = (res) => {
        if (res) {
            if (res.status === OK) {
                this.setState({after_adding_msg: "Product added Successfully", after_adding_msg_color: "primary"})
                if (this.props.getUserId() === -1) {
                    this.props.updateParent(res)
                }
            } else if (res.status === CONFLICT) {
                this.setState({
                    after_adding_msg: `ERROR: product no longer available`,
                    after_adding_msg_color: "danger"
                })
            } else {
                this.setState({after_adding_msg: `ERROR ${res.data["error"]}`, after_adding_msg_color: "danger"})
            }
        }
    };

    onChange = (e) => {
        this.setState({[e.target.name]: e.target.value});
    }

    decrease = () => {
        if (this.state.value_to_cart > 1) {
            this.setState({value_to_cart: this.state.value_to_cart - 1});

        }
    }

    increase = () => {
        this.setState({value_to_cart: this.state.value_to_cart + 1});
    }

    retrieveProductInfo = () => {
        let product_name = this.props.match.params.product_name
        let store_name = this.props.match.params.store_name
        let user_id = this.props.getUserId()
        console.log("test print:" + product_name)
        axios.get(
            `/get_product_info_view`,
            {
                params: {
                    user_id: user_id,
                    store_name: store_name.trim(),
                    product_name: product_name.trim()
                }
            }
        )
            .then((res) => {
                console.log(res)
                this.dealWithProductResult(res);
            }).catch(error => {
            console.log(error)
            this.dealWithProductResult(error.response);
        });
    }

    dealWithProductResult = (res) => {
        if (res) {
            console.log(res)
            if (res.status === OK) {
                let search_result = res.data["product_info"]
                this.setState({
                    productName: search_result["product"]["name"],
                    storeName: search_result["store_name"],
                    price: search_result["price"],
                    after_discount: search_result["after_discount"],
                    quantity: search_result["quantity"],
                    productBrand: search_result["product"]["brand"],
                    description: search_result["product"]["description"],
                    productCategories: search_result["product"]["categories"].reduce((acc, curr) => {
                        if (acc === "") {
                            return curr;
                        } else {
                            return `${acc},${curr}`
                        }
                    }, ""),
                    discounts: search_result["discounts"],
                    policies: search_result["policies"].map((policy, i) => `${i + 1}) ${policy}`).reduce((acc, curr) => `${acc}.\n${curr}`, '')
                })
                if (this.props.getUserId() === -1) {
                    this.props.updateParent(res)
                }

            } else {
                this.setState({msg: res.data["error"]})
            }
        }

    }

    getAlert = () => {
        if (this.state.after_adding_msg.length > 0) {
            return (<MDBAlert color={this.state.after_adding_msg_color}>
                {this.state.after_adding_msg}
            </MDBAlert>)
        }
    }

    render_discounts = () => {
        return (<React.Fragment>
            <h4>Discounts:</h4>
            {this.state.discounts.map((discount, i) => {
                    return <p className="lead">
                        {`${i + 1}) ${discount}`}
                    </p>

                }
            )
            }
        </React.Fragment>)

    }

    render_price = () => {
        if (this.state.after_discount !== this.state.price) {
            return (<React.Fragment>
                <hr className="my-2"/>
                {this.render_discounts()}
                <hr className="my-2"/>
                <p className="lead orange">
                    {`${this.state.after_discount}$`}
                </p>
                <p className="lead" style={{textDecorationLine: 'line-through', textDecorationStyle: 'solid'}}>
                    {`${this.state.price}$`}
                </p>
            </React.Fragment>);

        } else if (this.state.discounts !== null && this.state.discounts !== "") {
            return (<React.Fragment>
                <hr className="my-2"/>
                {this.render_discounts()}
                <hr className="my-2"/>
                <p className="lead">
                    {`${this.state.price}$`}
                </p>
            </React.Fragment>);
        } else {
            return (<React.Fragment>
                <hr className="my-2"/>
                <p className="lead">
                    {`${this.state.price}$`}
                </p>
            </React.Fragment>);
        }
    }

    render() {
        if (this.state.redirectAddress != null) {
            return <Redirect to={this.state.redirectAddress}/>
        } else {
            if ((this.state.productName === "") && this.state.msg === "") {
                this.retrieveProductInfo();
            }
            if (this.state.msg !== "") {
                return (
                    <MDBContainer>

                        <MDBRow style={{
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                        }}>
                            <h1>{this.state.msg}</h1>
                        </MDBRow>
                    </MDBContainer>
                );
            }
            return (
                <MDBContainer className="mt-5 text-center">
                    <MDBRow style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                    }}>
                        <MDBCol>
                            <MDBJumbotron>
                                <h2 className="h2 display-3">{this.state.productName}</h2>
                                <p className="lead">
                                    {this.state.description ? `${this.state.description}` : `No description for this product`}
                                </p>
                                <hr className="my-2"/>
                                <h6 className="lead">
                                    <MDBNavLink
                                        to={`/store_page/${this.state.storeName}`}> Store: {this.state.storeName}</MDBNavLink>
                                </h6>
                                <hr className="my-2"/>
                                <p>
                                    {this.state.productBrand ? `Brand: ${this.state.productBrand}` : `Brand: None`}
                                </p>
                                <hr className="my-2"/>
                                <p>
                                    {this.state.productCategories ? `Categories: ${this.state.productCategories}` : `Categories: None`}
                                </p>
                                <hr className="my-2"/>
                                <p className="lead">
                                    {this.state.quantity <= 10 ? `Quantity: only ${this.state.quantity} left!` : `Quantity: ${this.state.quantity}`}
                                </p>
                                <hr className="my-2"/>
                                <p>
                                    {this.state.policies ? `Policies: ${this.state.policies}` : `Policies: None`}
                                </p>
                                {this.render_price()}
                                <p className="lead">
                                    <div className="def-number-input number-input">
                                        <button onClick={this.decrease} className="minus">-</button>
                                        <input className="quantity" name="value_to_cart"
                                               value={this.state.value_to_cart}
                                               onChange={this.onChange}
                                               type="number"/>
                                        <button onClick={this.increase} className="plus">+</button>
                                    </div>
                                </p>

                                <MDBBtn onClick={this.addToShoppingCart} color="orange"><MDBIcon icon="cart-plus"
                                                                                                 size="3x"/></MDBBtn>
                                {this.getAlert()}

                            </MDBJumbotron>
                        </MDBCol>
                    </MDBRow>
                </MDBContainer>
            );
        }

    }
}

// PropTypes
ViewProductPage.propTypes = {
    productName: PropTypes.string.isRequired,
    storeName: PropTypes.string.isRequired,
    updateParent: PropTypes.func.isRequired,
    getUserId: PropTypes.func.isRequired,
};

export default withRouter(ViewProductPage);


